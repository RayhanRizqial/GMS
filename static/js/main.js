// static/js/main.js
document.addEventListener('DOMContentLoaded', () => {
    const currentPage = window.location.pathname;
    const menuItems = {
      '/dashboard': 'dashboard',
      '/tanya-nekobot': 'tanya-nekobot',
      '/model-pembanding': 'model-pembanding',
      '/info-management': 'info-management',
      '/fine-tuning': 'fine-tuning',
      '/vector-stores': 'vector-stores',
      '/model-configuration': 'model-configuration'
    };
  
    const activeMenuItem = menuItems[currentPage];
    if (activeMenuItem) {
      document.getElementById(activeMenuItem).classList.add('active');
    }
  });

  