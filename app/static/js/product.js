


const quantity_product = document.querySelector('#quantity_product');
const change_price = document.querySelector('#change-price');
// const quantity_product = document.querySelector('#quantity_product');


quantity_product.addEventListener('change', event => {
    
    
  result = parseInt(quantity_product.value) * parseInt(change_price.value);
  document.getElementById('change-price').value = parseInt(result);
     
    
    
})


const fileInput = document.getElementById('file-input');
const fileList = document.getElementById('file-list');
const uploadForm = document.getElementById('file-upload-form');

uploadForm.addEventListener('submit', async (e) => {
    e.preventDefault();
    const file = fileInput.files[0];
    const postId = 1; // Nahraďte ID príspevku, ku ktorému chcete priradiť súbor

    const formData = new FormData();
    formData.append('file', file);
    formData.append('post_id', postId);

    try {
        const response = await fetch('/upload', {
            method: 'POST',
            body: formData,
        });
        if (response.ok) {
            const data = await response.json();
            if (data.success) {
                // Súbor bol úspešne nahratý, aktualizujte zoznam súborov
                const listItem = document.createElement('li');
                listItem.innerHTML = `<a href="/uploads/${data.filename}" target="_blank">${data.filename}</a>`;
                fileList.appendChild(listItem);
            } else {
                console.error('Nahrávanie súboru zlyhalo.');
            }
        } else {
            console.error('Chyba servera pri nahrávaní súboru.');
        }
    } catch (error) {
        console.error('Nastala chyba pri nahrávaní súboru:', error);
    }
});
