// 페이지네이션 버튼 렌더링
function renderPagination() {
    const totalPages = Math.ceil(pagenation_list.length / rowsPerPage);
    const pagination = document.getElementById('pagination');
    const maxPagesToShow = 10; // 한 번에 표시할 최대 페이지 수
    const startPage = Math.floor((currentPage - 1) / maxPagesToShow) * maxPagesToShow + 1;
    const endPage = Math.min(startPage + maxPagesToShow - 1, totalPages);

    pagination.innerHTML = '';

    // "맨 앞" 버튼 추가
    pagination.innerHTML += `
        <li class="page-item ${currentPage === 1 ? 'disabled' : ''}">
            <a class="page-link" href="#" onclick="${currentPage !== 1 ? `changePage(1)` : 'return false;'}">맨 앞</a>
        </li>
    `;

    // "이전" 버튼 추가
    pagination.innerHTML += `
        <li class="page-item ${startPage === 1 ? 'disabled' : ''}">
            <a class="page-link" href="#" onclick="${startPage !== 1 ? `changePage(${startPage - 1})` : 'return false;'}">이전</a>
        </li>
    `;

    // 페이지 번호 추가
    for (let i = startPage; i <= endPage; i++) {
        const activeClass = i === currentPage ? 'active' : '';
        pagination.innerHTML += `
            <li class="page-item ${activeClass}">
                <a class="page-link" href="#" onclick="changePage(${i})">${i}</a>
            </li>
        `;
    }

    // "다음" 버튼 추가
    pagination.innerHTML += `
        <li class="page-item ${endPage === totalPages ? 'disabled' : ''}">
            <a class="page-link" href="#" onclick="${endPage !== totalPages ? `changePage(${endPage + 1})` : 'return false;'}">다음</a>
        </li>
    `;

    // "맨 끝" 버튼 추가
    pagination.innerHTML += `
        <li class="page-item ${currentPage === totalPages ? 'disabled' : ''}">
            <a class="page-link" href="#" onclick="${currentPage !== totalPages ? `changePage(${totalPages})` : 'return false;'}">맨 끝</a>
        </li>
    `;
}

// 페이지 변경
function changePage(page) {
    currentPage = page;
    renderTable(page);
    renderPagination();
}

