document.querySelectorAll('#loginForm, #registerForm').forEach(form => {
    form.addEventListener('submit', async function(e) {
        e.preventDefault();
        
        const existingError = this.querySelector('.alert-danger');
        if (existingError) {
            existingError.remove();
        }
        
        try {
            const formData = new FormData(this);
            const response = await fetch(this.action, {
                method: 'POST',
                body: formData,
                headers: {
                    'X-Requested-With': 'XMLHttpRequest'
                },
                credentials: 'same-origin'
            });
            
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            
            const data = await response.json();
            
            if (data.success) {
                if (this.id === 'registerForm') {
                    const submitBtn = this.querySelector('button[type="submit"]');
                    const originalText = submitBtn.textContent;
                    submitBtn.disabled = true;
                    
                    const successDiv = document.createElement('div');
                    successDiv.className = 'alert alert-success';
                    successDiv.style.marginBottom = '1rem';
                    
                    let countdown = 5;
                    const updateCountdown = () => {
                        successDiv.textContent = `注册成功！${countdown} 秒后自动跳转到登录...`;
                        if (countdown <= 0) {
                            switchModal('loginModal');
                            submitBtn.textContent = originalText;
                            submitBtn.disabled = false;
                            form.reset();
                        } else {
                            countdown--;
                            setTimeout(updateCountdown, 1000);
                        }
                    };
                    
                    const submitButton = this.querySelector('.d-grid');
                    submitButton.insertAdjacentElement('beforebegin', successDiv);
                    updateCountdown();
                } else {
                    if (data.redirect) {
                        window.location.href = data.redirect;
                    } else {
                        window.location.reload();
                    }
                }
            } else {
                const errorDiv = document.createElement('div');
                errorDiv.className = 'alert alert-danger';
                errorDiv.style.marginBottom = '1rem';
                errorDiv.textContent = data.message || '操作失败，请重试';
                
                const submitButton = this.querySelector('.d-grid');
                if (submitButton) {
                    submitButton.insertAdjacentElement('beforebegin', errorDiv);
                } else {
                    this.insertAdjacentElement('beforeend', errorDiv);
                }
            }
        } catch (error) {
            console.error('Error:', error);
            const errorDiv = document.createElement('div');
            errorDiv.className = 'alert alert-danger';
            errorDiv.style.marginBottom = '1rem';
            if (error.message.includes('HTTP error')) {
                errorDiv.textContent = '服务器响应错误，请稍后重试';
            } else if (error.name === 'TypeError') {
                errorDiv.textContent = '网络连接错误，请检查网络连接';
            } else {
                errorDiv.textContent = '发生错误，请稍后重试';
            }
            
            const submitButton = this.querySelector('.d-grid');
            if (submitButton) {
                submitButton.insertAdjacentElement('beforebegin', errorDiv);
            } else {
                this.insertAdjacentElement('beforeend', errorDiv);
            }
        }
    });
}); 