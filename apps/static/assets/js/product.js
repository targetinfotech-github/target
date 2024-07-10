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
input_record.style.display = 'none';
delete_record.style.display = 'none';

function selectManufacturer(id, related) {
    console.log(`id:${id} , related: ${related}`)
    var selectedRow = document.getElementById('row-' + id);
    if (!isNaN(parseInt(related)) & parseInt(related) === 0) {
        removable = true;
    } else {
        removable = false;
    }

    delete_record.style.display = 'none';
    console.log(id)
    if (selectedRowId === id) {
        // Deselect the row
        selectedRow.classList.remove('selected-row');
        input_record.value = '';
        delete_record.value = ''
        delete_record.style.display = 'none'
        input_record.style.display = 'none';

        selectedRowId = null;
    } else {
        if (selectedRowId !== null) {
            document.getElementById('row-' + selectedRowId).classList.remove('selected-row');
        }

        selectedRow.classList.add('selected-row');

        input_record.value = id;
        delete_record.value = id;
        input_record.style.display = '';
        if (removable) {
            delete_record.style.display = ''
        }

        selectedRowId = id;
    }
}


function selectProduct(id) {
    var selectedRow = document.getElementById('row-' + id);

    if (selectedRowId === id) {
        // Deselect the row
        selectedRow.classList.remove('selected-row');
        input_record.value = '';
        delete_record.value = ''
        delete_record.style.display = 'none'
        input_record.style.display = 'none';

        selectedRowId = null;
    } else {
        if (selectedRowId !== null) {
            document.getElementById('row-' + selectedRowId).classList.remove('selected-row');
        }

        selectedRow.classList.add('selected-row');

        input_record.value = id;
        delete_record.value = id;
        input_record.style.display = '';
        delete_record.style.display = ''

        selectedRowId = id;
    }
}


function selectCustomer(id, related) {
    var selectedRow = document.getElementById('row-' + id);

    if (selectedRowId === id) {
        // Deselect the row
        selectedRow.classList.remove('selected-row');
        input_record.value = '';
        delete_record.value = ''
        delete_record.style.display = 'none'
        input_record.style.display = 'none';

        selectedRowId = null;
    } else {
        if (selectedRowId !== null) {
            document.getElementById('row-' + selectedRowId).classList.remove('selected-row');
        }

        selectedRow.classList.add('selected-row');

        input_record.value = id;
        delete_record.value = id;
        input_record.style.display = '';
        delete_record.style.display = ''

        selectedRowId = id;
    }
}


function selectGroup(id, related) {
    console.log(`id:${id}, related:${related}`)
    var selectedRow = document.getElementById('row-' + id);
    if (!isNaN(parseInt(related)) & parseInt(related) === 0) {
        removable = true;
    } else {
        removable = false;
    }

    delete_record.style.display = 'none';
    if (selectedRowId === id) {
        // Deselect the row
        selectedRow.classList.remove('selected-row');
        input_record.value = '';
        delete_record.value = ''
        delete_record.style.display = 'none'
        input_record.style.display = 'none';

        selectedRowId = null;
    } else {
        if (selectedRowId !== null) {
            document.getElementById('row-' + selectedRowId).classList.remove('selected-row');
        }

        selectedRow.classList.add('selected-row');

        input_record.value = id;
        delete_record.value = id;
        input_record.style.display = '';
        if (removable) {
            delete_record.style.display = ''
        }
        selectedRowId = id;
    }
}

delete_record.addEventListener('click', function (event) {
    var confirmation = confirm('Are you sure you want to delete this record?');
    if (!confirmation) {
        event.preventDefault(); // Prevent form submission if the user cancels
    }
});