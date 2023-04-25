var stripe = Stripe(checkout_publick_key);

const button = document.querySelector('#buy_now_btn');

button.addEventListener('click', event => {

    amount_product = $('#amount_product').val();
    price_product = $('#price_product').val();
    id_product = $('#id_product').val();
    alert(price_product);

    $.ajax({
        url:"/products",
        type:"POST",
        data:{price_product:price_product},
        success:function()
        {

          setTimeout(function(){
        
        }, 2500);
        }
        });


    // stripe.redirectToCheckout({
    //     sessionId: checkout_session_id

    // }).then(function (result){

    //    var ide_product = document.querySelector('#ide_product').value;

    // })
})
