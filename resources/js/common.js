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

// 사이드바 토글 기능
function toggleSidebar() {
    const sidebar = document.querySelector('.sidebar');
    const mainContent = document.querySelector('.main-content');
    sidebar.classList.toggle('hidden');
    mainContent.classList.toggle('full-width');
}


//사용자 정보 페이지로 이동
function ViewUserInfo(customerId) {
    // 상세 보기 페이지로 이동
    window.location.href = `/user_billing/${customerId}`;
}

// 청구 정보 페이지로 이동
function ViewBillingInfo(totalchargeId) {
    window.location.href = `/billing_info/${totalchargeId}`;
}

// 이전 페이지로 이동    
function goBack() {
    history.back();
}



// 상세 보기
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


