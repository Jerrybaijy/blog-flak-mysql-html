function switchModal(targetModalId) {
    const currentModal = document.querySelector('.modal.show');
    const currentModalInstance = bootstrap.Modal.getInstance(currentModal);
    if (currentModalInstance) {
        currentModalInstance.hide();
    }
    
    setTimeout(() => {
        const targetModal = new bootstrap.Modal(document.getElementById(targetModalId));
        targetModal.show();
    }, 300);
} 