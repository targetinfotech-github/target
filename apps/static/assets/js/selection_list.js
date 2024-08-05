document.addEventListener('DOMContentLoaded', function () {
    console.log('DOM fully loaded and parsed');
    // Trigger the modal when the page loads
    var myModal = new bootstrap.Modal(document.getElementById('exampleModalCenter'), {
        backdrop: 'static',
        keyboard: false
    });
    myModal.show();
});
var input_record = document.getElementById('submit_selected_record');
var delete_record = document.getElementById('delete_selected_record');
var selectedRowId = null;
if (input_record) {
    input_record.style.display = 'none';

}
if (delete_record) {
    delete_record.style.display = 'none';

}

function selectList(id) {
    var selectedRow = document.getElementById('row-' + id);

    if (selectedRowId === id) {
        // Deselect the row
        selectedRow.classList.remove('selected-row');
        if (input_record) {
            input_record.value = '';
            input_record.style.display = 'none';
        }
        if (delete_record) {
            delete_record.value = ''
            delete_record.style.display = 'none'
        }

        selectedRowId = null;
    } else {
        if (selectedRowId !== null) {
            document.getElementById('row-' + selectedRowId).classList.remove('selected-row');
        }

        selectedRow.classList.add('selected-row');
        if (input_record) {
            input_record.value = id;
            input_record.style.display = '';

        }
        if (delete_record) {
            delete_record.value = id;
            delete_record.style.display = ''
        }


        selectedRowId = id;
    }
}


delete_record.addEventListener('click', function (event) {
    var confirmation = confirm('Are you sure you want to delete this record?');
    if (!confirmation) {
        event.preventDefault();
    }
});
