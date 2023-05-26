



// const button_add_to_basket = document.querySelector('#add_to_basket_btn');
const button_buy_now = document.querySelector('#buy_now_btn');

// button_add_to_basket.addEventListener('click', event => {
    
//     quantity_product = $('#quantity_product').val();
//     price_product = $('#price_product').val();
//     id_product = $('#id_product').val();
    
//     $.ajax({
//         url:"/products/basket",
//         type:"POST",
//         data:{
//             id_product:id_product
//         },
//         success:function()
//         {
    
//             setTimeout(function(){
    
//             }, 2500);
//         }
//     });
    
// })

var stripe = Stripe(checkout_publick_key);
    button_buy_now.addEventListener('click', event => {

    // quantity_product = $('#quantity_product').val();
    // price_product = $('#price_product').val();
    // id_product = $('#id_product').val();
    // alert(price_product);

    // $.ajax({
    //     url:"/products",
    //     type:"POST",
    //     data:{price_product:price_product},
    //     success:function()
    //     {

    //       setTimeout(function(){
        
    //     }, 2500);
    //     }
    //     });


    stripe.redirectToCheckout({
        sessionId: checkout_session_id

    }).then(function (result){

    //    var ide_product = document.querySelector('#ide_product').value;

    })
})
