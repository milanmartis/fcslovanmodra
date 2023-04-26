

const quantity_product = document.querySelector('#quantity_product');
const change_price = document.querySelector('#change-price');
// const quantity_product = document.querySelector('#quantity_product');


quantity_product.addEventListener('change', event => {
    
    
  result = parseInt(quantity_product.value) * parseInt(change_price.value);
  document.getElementById('change-price').value = parseInt(result);
     
    
    
})