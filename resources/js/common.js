// Flatpickr 라이브러리 설정 
document.addEventListener('DOMContentLoaded', function () {
    const startDateElement = document.getElementById('start_date');
    const endDateElement = document.getElementById('end_date');

    if (startDateElement && endDateElement) {
        flatpickr(startDateElement, {
            dateFormat: "Y-m",
            plugins: [
                new monthSelectPlugin({
                    shorthand: true,
                    dateFormat: "Y-m",
                })
            ],
            onChange: function (selectedDates, dateStr) {
                const intDate = dateStr.replace("-", "");
                startDateElement.dataset.intValue = intDate;
            }
        });

        flatpickr(endDateElement, {
            dateFormat: "Y-m",
            plugins: [
                new monthSelectPlugin({
                    shorthand: true,
                    dateFormat: "Y-m",
                })
            ],
            onChange: function (selectedDates, dateStr) {
                const intDate = dateStr.replace("-", "");
                endDateElement.dataset.intValue = intDate;
            }
        });
    } else {
        console.error("Date elements are not found.");
    }
});

// 상세 보기 버튼 동작 
document.getElementById('toggleDetails').addEventListener('click', function() {
    const detailRows = document.querySelectorAll('.detail-table');
    detailRows.forEach(row => {
        if (row.style.display === 'none') {
            row.style.display = '';
        } else {
            row.style.display = 'none';
        }
    });
});

// 체크 박스 전체 선택
function toggleAllCheckboxes(groupName) {
    const allCheckbox = document.querySelector(`input[name="${groupName}-all"]`);
    const checkboxes = document.querySelectorAll(`input[name="${groupName}"]`);
    checkboxes.forEach(checkbox => checkbox.checked = allCheckbox.checked);
}

// "전체 선택" 체크 박스와 개별 체크 박스 상태 동기화
function updateSelectAllCheckbox(groupName) {
    const allCheckbox = document.querySelector(`input[name="${groupName}-all"]`);
    const checkboxes = document.querySelectorAll(`input[name="${groupName}"]`);
    allCheckbox.checked = Array.from(checkboxes).every(checkbox => checkbox.checked);
}

// 시작 날짜와 종료 날짜가 유효한지 확인
function validateDates() {

    const startInt = parseInt(document.getElementById('start_date').value.replace("-",""), 10);
    const endInt = parseInt(document.getElementById('end_date').value.replace("-",""), 10);

    // 오늘 날짜를 가져와 숫자로 변환 (YYYYMMDD 형식)
    const today = new Date();
    // 날짜를 "Ym" 형식으로 변환
    const formatDateToInt = (date) => {
        const year = date.getFullYear();
        const month = String(date.getMonth() + 1).padStart(2, '0'); // 월은 0부터 시작하므로 +1
        return parseInt(`${year}${month}`, 10); // 정수로 변환
    };

    const todayInt = formatDateToInt(today); // 오늘 날짜

    // 시작 날짜가 종료 날짜보다 늦는지 확인
    if (startInt > endInt) {
        alert('시작 날짜가 종료 날짜보다 늦을 수 없습니다.');
        return false;
    }

    // 시작 날짜와 종료 날짜가 오늘보다 늦는지 확인
    if (startInt > todayInt || endInt > todayInt) {
        alert('시작 날짜와 종료 날짜는 오늘보다 늦을 수 없습니다.');
        return false;
    }

    return true;
}

// 조회 기간 초기화
function resetDate() {
    const today = new Date();
    const oneYearAgo = new Date(today.getFullYear() - 1, today.getMonth());

    // 날짜를 "Ym" 형식으로 변환
    const formatDateToInt = (date) => {
        const year = date.getFullYear();
        const month = String(date.getMonth() + 1).padStart(2, '0'); // 월은 0부터 시작하므로 +1
        return parseInt(`${year}${month}`, 10); // 정수로 변환
    };

    const startInt = formatDateToInt(oneYearAgo); // 1년 전
    const endInt = formatDateToInt(today);       // 현재

    // input 요소에 값을 설정
    document.getElementById('start_date').value = `${oneYearAgo.getFullYear()}-${String(oneYearAgo.getMonth() + 1).padStart(2, '0')}`;
    document.getElementById('start_date').dataset.intValue = startInt; // int 값 저장

    document.getElementById('end_date').value = `${today.getFullYear()}-${String(today.getMonth() + 1).padStart(2, '0')}`;
    document.getElementById('end_date').dataset.intValue = endInt; // int 값 저장
}

// 사용자 리스트의 필터 초기화
function ResetUserListFilters() {
    // 검색 필드 초기화
    document.getElementById('customer-name').value = '';

    // 구분 및 클라우드사 전체 체크
    document.getElementById('category-all').checked = true;
    toggleAllCheckboxes('category');

    document.getElementById('cloud-all').checked = true;
    toggleAllCheckboxes('cloud-company');
}

// 청구 리스트의 필터 초기화
function ResetBillingListFilters() {
    // 검색 필드 초기화
    document.getElementById('customer-name').value = '';

    // 조회 기간 초기화 
    resetDate()

    // 구분 및 클라우드사 전체 체크
    document.getElementById('category-all').checked = true;
    toggleAllCheckboxes('category');

    document.getElementById('cloud-all').checked = true;
    toggleAllCheckboxes('cloud-company');

}

function applyFilterDict() {
    if (filter_dict) {
        // class_list 체크박스 설정
        if (filter_dict.class_list) {
            filter_dict.class_list.forEach(value => {
                const checkbox = document.querySelector(`input[name="category"][value="${value}"]`);
                if (checkbox) {
                    checkbox.checked = true;
                }
            });
        }
        updateSelectAllCheckbox('category')
        // cloud_list 체크박스 설정
        if (filter_dict.cloud_list) {
            filter_dict.cloud_list.forEach(value => {
                const checkbox = document.querySelector(`input[name="cloud-company"][value="${value}"]`);
                if (checkbox) {
                    checkbox.checked = true;
                }
            });
        }
        updateSelectAllCheckbox('cloud-company')

        // user_name 입력 필드 설정
        if (filter_dict.user_name) {
            const inputField = document.getElementById('customer-name');
            if (inputField) {
                inputField.value = filter_dict.user_name;
            }
        }
    }
}


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

function submitForm() {
    if (validateDates()) {
        // 검증이 통과되면 폼 제출
        document.querySelector('form').submit();
    }
}


// 청구 리스트 조회
function BillingListSearch() {
    if (!validateDates()) return;
    currentPage = 1;
    renderTable(currentPage);
    // 페이지를 1페이지로 초기화
    renderPagination();

    const customerName = document.getElementById('customer-name').value.toLowerCase();

    // 선택된 구분 체크박스 값 가져오기
    const selectedCategories = Array.from(document.querySelectorAll('input[name="category"]:checked'))
        .map(checkbox => checkbox.value);

    // 선택된 클라우드사 체크박스 값 가져오기
    const selectedClouds = Array.from(document.querySelectorAll('input[name="cloud-company"]:checked'))
        .map(checkbox => checkbox.value);

    // 선택된 조회 기간 값 가져오기
    const startInt = parseInt(document.getElementById('start_date').value.replace("-", ""), 10);
    const endInt = parseInt(document.getElementById('end_date').value.replace("-", ""), 10);

    const table = document.getElementById('billing-table');
    const rows = table.getElementsByTagName('tr');

    for (let i = 0; i < rows.length; i++) {
        const cells = rows[i].getElementsByTagName('td');
        if (cells.length > 0) {

            const name = cells[1].textContent.toLowerCase(); // 고객사명은 셀의 2번째 열
            const cat = cells[2].textContent;
            const cloud = cells[3].textContent;
            const dateCell = cells[4].textContent; // 기간 열 (5번째 열)
            const billMonth = dateCell.trim().replace("년 ", "").replace("월", "");
            const billMonthInt = parseInt(billMonth, 10);

            const matchesName = !customerName || name.includes(customerName);
            const matchesCategory = selectedCategories.length === 0 || selectedCategories.some(category => cat.includes(category));
            const matchesCloud = selectedClouds.length === 0 || selectedClouds.some(cloudCompany => cloud.includes(cloudCompany));
            const matchesBillMonth = billMonthInt >= startInt && billMonthInt <= endInt

            if (matchesName && matchesCategory && matchesCloud && matchesBillMonth) {
                rows[i].style.display = '';
            } else {
                rows[i].style.display = 'none';
            }
        }
    }
}


//사용자 정보 페이지로 이동
function ViewUserInfo(customerId) {
    // 상세 보기 페이지로 이동
    window.location.href = `/user_info/${customerId}`;
}

// 청구 정보 페이지로 이동
function ViewBillingInfo(totalchargeId) {
    window.location.href = `/billing_info/${totalchargeId}`;
}

// 이전 페이지로 이동    
function goBack() {
    history.back();
}

// 사이드바 토글 기능
function toggleSidebar() {
    const sidebar = document.querySelector('.sidebar');
    const mainContent = document.querySelector('.main-content');
    sidebar.classList.toggle('hidden');
    mainContent.classList.toggle('full-width');
}
