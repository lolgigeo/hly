// 搜索功能
(function() {
  'use strict';

  const searchInput = document.getElementById('search-input');
  const searchResults = document.getElementById('search-results');
  const chaptersList = document.getElementById('chapters-list');
  
  if (!searchInput || !searchResults || !chaptersList) {
    return;
  }

  // 获取所有章节数据
  const chapters = Array.from(document.querySelectorAll('.chapter-card')).map(card => {
    return {
      element: card,
      chapter: parseInt(card.dataset.chapter),
      title: card.dataset.title,
      text: card.textContent.toLowerCase()
    };
  });

  // 搜索函数
  function performSearch(query) {
    const searchTerm = query.toLowerCase().trim();
    
    if (searchTerm.length === 0) {
      searchResults.classList.remove('active');
      searchResults.innerHTML = '';
      chapters.forEach(ch => ch.element.style.display = '');
      return;
    }

    // 过滤章节
    const matchedChapters = chapters.filter(ch => {
      return ch.title.toLowerCase().includes(searchTerm) || 
             ch.text.includes(searchTerm) ||
             ch.chapter.toString().includes(searchTerm);
    });

    // 显示/隐藏章节卡片
    chapters.forEach(ch => {
      if (matchedChapters.includes(ch)) {
        ch.element.style.display = '';
      } else {
        ch.element.style.display = 'none';
      }
    });

    // 显示搜索结果摘要
    if (matchedChapters.length > 0) {
      searchResults.classList.add('active');
      searchResults.innerHTML = `<p style="padding: 10px; color: #666;">找到 ${matchedChapters.length} 个匹配的章节</p>`;
    } else {
      searchResults.classList.add('active');
      searchResults.innerHTML = `<p style="padding: 10px; color: #999;">未找到匹配的章节</p>`;
    }
  }

  // 防抖函数
  function debounce(func, wait) {
    let timeout;
    return function executedFunction(...args) {
      const later = () => {
        clearTimeout(timeout);
        func(...args);
      };
      clearTimeout(timeout);
      timeout = setTimeout(later, wait);
    };
  }

  // 绑定搜索事件
  const debouncedSearch = debounce(performSearch, 300);
  
  searchInput.addEventListener('input', function() {
    debouncedSearch(this.value);
  });

  // 回车键快速跳转
  searchInput.addEventListener('keydown', function(e) {
    if (e.key === 'Enter') {
      e.preventDefault();
      const firstMatch = chapters.find(ch => 
        ch.element.style.display !== 'none'
      );
      if (firstMatch) {
        const link = firstMatch.element.querySelector('.chapter-link');
        if (link) {
          window.location.href = link.href;
        }
      }
    }
  });

  // 清除搜索
  searchInput.addEventListener('focus', function() {
    if (this.value.length > 0) {
      performSearch(this.value);
    }
  });
})();
