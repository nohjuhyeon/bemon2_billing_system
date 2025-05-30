// 버튼 동작 함수
document.addEventListener('DOMContentLoaded', () => {
    function summarySetupForm(formId, editButtonId, saveButtonId, cancelButtonId, valueData, inputData, collectionName) {
        const form = document.getElementById(formId);
        const editButton = document.getElementById(editButtonId);
        const saveButton = document.getElementById(saveButtonId);
        const cancelButton = document.getElementById(cancelButtonId);
        const summaryTable = form.querySelector("tbody");
        const valueCells = form.querySelectorAll(valueData);
        const inputCells = form.querySelectorAll(inputData);
        const originalValues = Array.from(inputCells).map(input => input.value.trim());

        editButton.addEventListener("click", () => {
            valueCells.forEach(cell => {
                cell.style.display = "none";
            });
            inputCells.forEach(cell => {
                cell.style.display = "block";
            });
            editButton.style.display = "none";
            saveButton.style.display = "block";
            cancelButton.style.display = "block";
        });

        cancelButton.addEventListener("click", () => {
            valueCells.forEach(cell => {
                cell.style.display = "block";
            });
            inputCells.forEach((cell, index) => {
                cell.value = originalValues[index]; // 원래 값 복원
                cell.style.display = "none";
            });
            editButton.style.display = "block";
            saveButton.style.display = "none";
            cancelButton.style.display = "none";
        });

    }

    summarySetupForm('totalSummaryForm', 'editButtonTotalSummary', 'saveButtonTotalSummary', 'cancelButtonTotalSummary', '#valueDataTotalSummary', '#inputDataTotalSummary', 'TOTAL');
    summarySetupForm('cloudSummaryForm', 'editButtonCloudSummary', 'saveButtonCloudSummary', 'cancelButtonCloudSummary', '#valueDataCloudSummary', '#inputDataCloudSummary', 'CLOUD');
});

// 버튼 동작 함수
document.addEventListener('DOMContentLoaded', () => {
    function collectionSetupForm(formId, editButtonId, saveButtonId, addButtonId, deleteButtonId, cancelButtonId, selectAllCheckboxId, valueData, inputData, collectionName) {
        const form = document.getElementById(formId);
        const editButton = document.getElementById(editButtonId);
        const saveButton = document.getElementById(saveButtonId);
        const addButton = document.getElementById(addButtonId);
        const deleteButton = document.getElementById(deleteButtonId);
        const cancelButton = document.getElementById(cancelButtonId);
        const selectAllCheckbox = document.getElementById(selectAllCheckboxId);
        const summaryTable = form.querySelector("tbody");
        const valueCells = form.querySelectorAll(valueData);
        const inputCells = form.querySelectorAll(inputData);
        let addedRows = [];
        let deletedRows = []; // 삭제된 행을 저장할 배열
        let rowCounter = 2;
        const originalValues = Array.from(inputCells).map(input => input.value.trim());

        editButton.addEventListener("click", () => {
            valueCells.forEach(cell => {
                cell.style.display = "none";
            });
            inputCells.forEach(cell => {
                cell.style.display = "block";
            });
            editButton.style.display = "none";
            addButton.style.display = "block";
            saveButton.style.display = "block";
            cancelButton.style.display = "block";
            deleteButton.style.display = "block";
            form.querySelectorAll(".row-select").forEach(checkbox => {
                checkbox.checked = false;
            });
        });

        cancelButton.addEventListener("click", () => {
            // 삭제된 행 복원
            deletedRows.forEach(row => {
                summaryTable.appendChild(row);
            });
            deletedRows = [];

            addedRows.forEach(row => {
                if (summaryTable.contains(row)) {
                    summaryTable.removeChild(row);
                }
            });
            addedRows = [];
            rowCounter = 2;
            valueCells.forEach(cell => {
                cell.style.display = "block";
            });
            inputCells.forEach((cell, index) => {
                cell.value = originalValues[index]; // 원래 값 복원
                cell.style.display = "none";
            });
            editButton.style.display = "block";
            addButton.style.display = "none";
            saveButton.style.display = "none";
            cancelButton.style.display = "none";
            deleteButton.style.display = "none";
            selectAllCheckbox.checked = false;
            form.querySelectorAll(".row-select").forEach(checkbox => {
                checkbox.checked = false;
            });
        });

        addButton.addEventListener("click", () => {
            const NEWRow = document.createElement("tr");
            NEWRow.classList.add("detail-row");

            NEWRow.innerHTML = `
    <td class="text-center">
        <input type="checkbox" class="row-select" style="display:block;">
    </td>
    <td class="text-center">
        <input type="text" class="form-control form-control-sm input-data" name="${collectionName}_CATEGORY_NEW_${rowCounter}">
    </td>
    <td class="text-center">
        <input type="text" class="form-control form-control-sm input-data" name="${collectionName}_PRODUCT_NAME_NEW_${rowCounter}">
    </td>
    <td class="text-right">
        <input type="text" class="form-control form-control-sm input-data" name="${collectionName}_USE_AMT_NEW_${rowCounter}">
    </td>
    <td class="text-right">
        <input type="text" class="form-control form-control-sm input-data" name="${collectionName}_USER_PAY_AMT_NEW_${rowCounter}">
    </td>
    <td class="text-right">
        <input type="text" class="form-control form-control-sm input-data" name="${collectionName}_NOTES_NEW_${rowCounter}">
    </td>
    `;

            summaryTable.appendChild(NEWRow);
            addedRows.push(NEWRow);
            rowCounter++;
        });

        deleteButton.addEventListener("click", () => {
            form.querySelectorAll(".row-select:checked").forEach(checkbox => {
                const row = checkbox.closest("tr");
                if (row && summaryTable.contains(row)) {
                    deletedRows.push(row); // 삭제된 행 저장
                    summaryTable.removeChild(row);
                }
            });
        });

        selectAllCheckbox.addEventListener("change", () => {
            const checked = selectAllCheckbox.checked;
            form.querySelectorAll(".row-select").forEach(checkbox => {
                checkbox.checked = checked;
            });
        });
    }

    collectionSetupForm('thirdPartyForm', 'editButtonThirdParty', 'saveButtonThirdParty', 'addButtonThirdParty', 'deleteButtonThirdParty', 'cancelButtonThirdParty', 'selectAllThirdParty', '#valueDataThirdParty', '#inputDataThirdParty', 'THIRD_PARTY');
    collectionSetupForm('managedServiceForm', 'editButtonManagedService', 'saveButtonManagedService', 'addButtonManagedService', 'deleteButtonManagedService', 'cancelButtonManagedService', 'selectAllManagedService', '#valueDataManagedService', '#inputDataManagedService', 'MANAGED_SERVICE');
    collectionSetupForm('otherServiceForm', 'editButtonOtherService', 'saveButtonOtherService', 'addButtonOtherService', 'deleteButtonOtherService', 'cancelButtonOtherService', 'selectAllOtherService', '#valueDataOtherService', '#inputDataOtherService', 'OTHER_SERVICE');

});






// 입력값에 대한 유효성 검사
function validateForm(formName) {
    const form = document.getElementById(formName);
    const useAmountInputs = form.querySelectorAll("input[name*='AMT']");
    const serviceInputs = form.querySelectorAll("input[name*='CATEGORY']");
    const productInputs = form.querySelectorAll("input[name*='PRODUCT_NAME']");
    
    // 서비스명 입력 검사
    for (let i = 0; i < serviceInputs.length; i++) {
        const input = serviceInputs[i];
        const value = input.value.trim();
        if (value === "") {
            alert(`서비스명을 입력해주세요.`);
            input.focus();
            return false; // 유효성 검사 실패 시 false 반환
        }
    }

    // 상품명 입력 검사
    for (let i = 0; i < productInputs.length; i++) {
        const input = productInputs[i];
        const value = input.value.trim();
        if (value === "") {
            alert(`상품명을 입력해주세요.`);
            input.focus();
            return false; // 유효성 검사 실패 시 false 반환
        }
    }

    // 금액 입력 검사
    for (let i = 0; i < useAmountInputs.length; i++) {
        const input = useAmountInputs[i];
        const value = input.value.trim();
        if (value === "" || isNaN(value)) {
            alert(`금액은 숫자여야 합니다.`);
            input.focus();
            return false; // 유효성 검사 실패 시 false 반환
        }
        else if (value.length > 11) {
            alert(`금액은 11자리 이하의 숫자여야 합니다.`);
            input.focus();
            return false; // 유효성 검사 실패 시 false 반환
    }

    }

    return true; // 모든 값이 유효하면 true 반환
}



// 입력값 업데이트
function updateForm(event, formName) {
    const isValid = validateForm(formName);
    console.log("Validation result:", isValid);

    if (!isValid) {
        if (event) {
            event.preventDefault();
            console.log("Form submission prevented.");
        }
    }

    return isValid; // 유효성 검사가 통과되면 true 반환하여 제출 허용
}