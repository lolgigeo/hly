// 章节导航功能
(function() {
  'use strict';

  // 键盘快捷键支持
  document.addEventListener('keydown', function(e) {
    // 只在章节页面启用快捷键
    if (!document.querySelector('.chapter-content')) {
      return;
    }

    // 左箭头：上一章
    if (e.key === 'ArrowLeft' || e.key === 'ArrowUp') {
      const prevBtn = document.querySelector('.btn-prev');
      if (prevBtn && !prevBtn.classList.contains('btn-disabled')) {
        e.preventDefault();
        window.location.href = prevBtn.href;
      }
    }

    // 右箭头：下一章
    if (e.key === 'ArrowRight' || e.key === 'ArrowDown') {
      const nextBtn = document.querySelector('.btn-next');
      if (nextBtn && !nextBtn.classList.contains('btn-disabled')) {
        e.preventDefault();
        window.location.href = nextBtn.href;
      }
    }

    // ESC：返回目录
    if (e.key === 'Escape') {
      const indexBtn = document.querySelector('.btn-index');
      if (indexBtn) {
        e.preventDefault();
        window.location.href = indexBtn.href;
      }
    }
  });

  // 平滑滚动
  document.querySelectorAll('a[href^="#"]').forEach(anchor => {
    anchor.addEventListener('click', function(e) {
      const href = this.getAttribute('href');
      if (href !== '#' && href.startsWith('#')) {
        e.preventDefault();
        const target = document.querySelector(href);
        if (target) {
          target.scrollIntoView({
            behavior: 'smooth',
            block: 'start'
          });
        }
      }
    });
  });

  // 移动端菜单切换
  const navTrigger = document.getElementById('nav-trigger');
  if (navTrigger) {
    navTrigger.addEventListener('change', function() {
      document.body.style.overflow = this.checked ? 'hidden' : '';
    });
  }
})();
