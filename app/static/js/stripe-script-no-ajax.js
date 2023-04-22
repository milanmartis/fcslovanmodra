var stripe = Stripe(checkout_publick_key);

const button = document.querySelector('#buy_now_btn');

button.addEventListener('click', event => {
    stripe.redirectToCheckout({
        sessionId: checkout_session_id

    }).then(function (result){

       // var ide_product = document.querySelector('#ide_product').value;

    })
})
