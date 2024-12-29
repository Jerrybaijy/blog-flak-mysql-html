from flask import Blueprint, render_template, flash, redirect, url_for, request, jsonify
from flask_login import login_user, logout_user, login_required, current_user
from app import db
from app.models import User, Post
from app.forms import LoginForm, RegistrationForm, PostForm
import os
from flask import current_app
from functools import wraps
from flask import session
import markdown
from datetime import datetime
import os.path
from mutagen import File
from mutagen.mp3 import MP3
from mutagen.id3 import ID3
import base64

main = Blueprint('main', __name__)

# 创建一个辅助函数来获取通用的模板参数
def get_template_context(title):
    return {
        'title': title,
        'login_form': LoginForm(),
        'register_form': RegistrationForm(),
    }

def login_required_with_next(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            # 保存用户想要访问的页面
            session['next'] = request.url
            # 返回需要登录的 JSON 响应
            return jsonify({
                'needLogin': True,
                'message': '请先登录'
            })
        return f(*args, **kwargs)
    return decorated_function

@main.route('/', endpoint='root')
@main.route('/index')
def index():
    context = get_template_context('首页')
    return render_template('index.html', **context)

@main.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    
    form = LoginForm()
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        user = User.query.filter_by(username=username).first()
        if user is None or not user.check_password(password):
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return jsonify({'success': False, 'message': '用户名或密码错误'})
            flash('用户名或密码错误')
            return redirect(url_for('main.login'))
            
        login_user(user)
        next_page = session.pop('next', None)
        
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return jsonify({'success': True, 'redirect': next_page if next_page else url_for('main.index')})
        
        return redirect(next_page if next_page else url_for('main.index'))
    
    context = get_template_context('登录')
    context['form'] = form
    return render_template('login.html', **context)

@main.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    
    form = RegistrationForm()
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        password2 = request.form.get('password2')
        
        try:
            if password != password2:
                if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                    return jsonify({'success': False, 'message': '两次输入的密码不一致'})
                flash('两次输入的密码不一致')
                return redirect(url_for('main.register'))
                
            if User.query.filter_by(username=username).first():
                if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                    return jsonify({'success': False, 'message': '用户名已被使用'})
                flash('用户名已被使用')
                return redirect(url_for('main.register'))
                
            if User.query.filter_by(email=email).first():
                if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                    return jsonify({'success': False, 'message': '邮箱已被注册'})
                flash('邮箱已被注册')
                return redirect(url_for('main.register'))
                
            user = User(username=username, email=email)
            user.set_password(password)
            
            # 使用事务
            try:
                db.session.add(user)
                db.session.commit()
                if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                    return jsonify({'success': True})
                flash('注册成功！')
                return redirect(url_for('main.login'))
            except Exception as e:
                db.session.rollback()
                if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                    return jsonify({'success': False, 'message': '数据库错误，请稍后重试'})
                flash('注册失败，请稍后重试')
                return redirect(url_for('main.register'))
                
        except Exception as e:
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return jsonify({'success': False, 'message': '服务器错误，请稍后重试'})
            flash('服务器错误，请稍后重试')
            return redirect(url_for('main.register'))
    
    context = get_template_context('注册')
    context['form'] = form
    return render_template('register.html', **context)

@main.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('main.root'))

@main.route('/create_post', methods=['GET', 'POST'])
@login_required
def create_post():
    form = PostForm()
    if form.validate_on_submit():
        post = Post(title=form.title.data, content=form.content.data, author=current_user)
        db.session.add(post)
        db.session.commit()
        flash('文章发布成功！')
        return redirect(url_for('main.index'))
    
    context = get_template_context('发布文章')
    context['form'] = form
    return render_template('create_post.html', **context)

@main.route('/post/<int:id>')
def post(id):
    post = Post.query.get_or_404(id)
    context = get_template_context(post.title)
    context['post'] = post
    return render_template('post.html', **context)

@main.route('/user/<username>')
@login_required
def user_profile(username):
    user = User.query.filter_by(username=username).first_or_404()
    posts = user.posts.order_by(Post.timestamp.desc()).all()
    context = get_template_context(f'{user.username}的个人主页')
    context['user'] = user
    context['posts'] = posts
    return render_template('user_profile.html', **context)

def get_music_list():
    """获取音乐文件夹中的所有音乐文件"""
    music_dir = os.path.join(current_app.static_folder, 'music')
    music_files = []
    
    if os.path.exists(music_dir):
        for file in os.listdir(music_dir):
            if file.lower().endswith(('.mp3', '.wav', '.ogg', '.m4a')):
                file_path = os.path.join(music_dir, file)
                play_path = url_for('static', filename=f'music/{file}')
                display_name = os.path.splitext(file)[0]
                
                # 获取专辑封面、标签和年份
                cover_data = None
                keywords = []
                year = None
                try:
                    if file.lower().endswith('.mp3'):
                        audio = MP3(file_path, ID3=ID3)
                        if audio.tags:
                            # 获取封面
                            for tag in audio.tags.values():
                                if tag.FrameID == 'APIC':
                                    cover_data = base64.b64encode(tag.data).decode('utf-8')
                                    break
                            
                            # 获取年份
                            for tag in audio.tags.values():
                                if tag.FrameID == 'TDRC':  # 录制年份
                                    year = str(tag.text[0])[:4]  # 只取年份部分
                                    break
                                elif tag.FrameID == 'TYER':  # 年份标签
                                    year = str(tag.text[0])
                                    break
                            
                            # 获取关键词
                            for tag in audio.tags.values():
                                if tag.FrameID == 'TXXX' and tag.desc.lower() == 'keywords':
                                    raw_keywords = tag.text[0]
                                    if '; ' in raw_keywords:
                                        keywords = [k.strip() for k in raw_keywords.split('; ')]
                                    elif ';' in raw_keywords:
                                        keywords = [k.strip() for k in raw_keywords.split(';')]
                                    elif ', ' in raw_keywords:
                                        keywords = [k.strip() for k in raw_keywords.split(', ')]
                                    elif ',' in raw_keywords:
                                        keywords = [k.strip() for k in raw_keywords.split(',')]
                                    else:
                                        keywords = [raw_keywords.strip()]
                                    break
                except Exception as e:
                    current_app.logger.error(f"Error reading tags for {file}: {e}")
                
                # 如果没有从标签中获取到年份，尝试从文件名中提取
                if not year:
                    # 尝试从文件名中匹配年份（4位数字）
                    import re
                    match = re.search(r'(19|20)\d{2}', display_name)
                    if match:
                        year = match.group(0)
                
                music_files.append({
                    'path': play_path,
                    'name': display_name,
                    'cover': cover_data,
                    'keywords': keywords,
                    'year': year or 'Unknown'  # 如果没有年份信息，显示 Unknown
                })
    
    return sorted(music_files, key=lambda x: x['name'])

@main.route('/music')
@login_required_with_next
def music():
    context = get_template_context('Music')
    context['music_files'] = get_music_list()
    context['current_year'] = datetime.now().year
    return render_template('music.html', **context)

def get_notes_list():
    """获取笔记文件夹中的所有 markdown 文件"""
    notes_dir = os.path.join(current_app.static_folder, 'notes')
    notes = []
    
    if os.path.exists(notes_dir):
        for file in os.listdir(notes_dir):
            if file.lower().endswith('.md'):
                file_path = os.path.join(notes_dir, file)
                # 获取文件修改时间
                modified_time = datetime.fromtimestamp(os.path.getmtime(file_path))
                # 使用文件名（不含扩展名）作为标题
                title = os.path.splitext(file)[0]
                # 读取文件内容获取预览
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                    # 获取预览内容（前200个字符）
                    preview = content.strip()[:200]
                
                notes.append({
                    'filename': file,
                    'title': title,
                    'preview': preview,
                    'modified_time': modified_time
                })
    
    return sorted(notes, key=lambda x: x['modified_time'], reverse=True)

@main.route('/note')
@login_required_with_next
def note():
    context = get_template_context('Note')
    context['notes'] = get_notes_list()
    return render_template('note.html', **context)

@main.route('/note/<filename>')
@login_required_with_next
def note_detail(filename):
    notes_dir = os.path.join(current_app.static_folder, 'notes')
    file_path = os.path.join(notes_dir, filename)
    
    if not os.path.exists(file_path):
        flash('笔记不存在')
        return redirect(url_for('main.note'))
    
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
        # 替换 HTML 格式的图片路径，使用完整的静态文件路径
        content = content.replace(
            'src="assets/',
            'src="/static/notes/assets/'
        )
        # 替换 style 属性中的 zoom
        content = content.replace('style="zoom:', 'style="width:')
        content = content.replace('%;', '%;height:auto;')
        
        html_content = markdown.markdown(
            content,
            extensions=[
                'fenced_code',
                'codehilite',
                'tables',
                'nl2br',
                'attr_list',
                'md_in_html'
            ]
        )
    
    context = get_template_context('Note')
    context['content'] = html_content
    context['title'] = os.path.splitext(filename)[0]
    return render_template('note_detail.html', **context)

@main.route('/article')
@login_required_with_next
def article():
    posts = Post.query.order_by(Post.timestamp.desc()).all()
    context = get_template_context('Article')
    context['posts'] = posts
    return render_template('article.html', **context) 