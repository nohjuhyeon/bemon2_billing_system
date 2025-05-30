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

// 필터링 상태 동기화
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

// 필터링 전송
function submitForm(event) {
    const isValid = validateDates();
    console.log("Validation result:", isValid);

    if (!isValid) {
        // 검증이 실패하면 기본 동작을 막음
        event.preventDefault();
        console.log("Form submission prevented due to invalid dates.");
    }

    return isValid;
}


