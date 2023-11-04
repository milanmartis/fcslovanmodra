document.addEventListener('DOMContentLoaded', () => {
    const customPaymentButton = document.getElementById('custom-payment-button');
    customPaymentButton.addEventListener('click', async () => {
      const customPrice = document.getElementById('final_price').value;
      const ideProduct = document.getElementById('ide_product').value;
      const productName = document.getElementById('name_product').value;
      const quantity = document.getElementById('quantity').value;
      const unit_price = document.getElementById('unit_price').value;
      const variantProductsList = document.getElementById('product-variant-send');
      const variantProductsList22 = variantProductsList.value;

     // alert(customPrice);

  
      // Volanie API na server pre vytvorenie platobnej relácie s vlastnou cenou a názvom produktu
      const response = await fetch('/product/create-custom-payment-session', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            customPrice,
            productName,
            ideProduct,
            variantProductsList22,
            quantity,
            unit_price

        }),
      });
  
      const session = await response.json();
  
      // Presmerovanie na platobnú stránku Stripe Checkout
      const stripe = Stripe(checkout_public_key);
      const { error } = await stripe.redirectToCheckout({
        sessionId: session.id,
      });
  
      // Spracovanie chýb
      if (error) {
        console.error(error);
      }
    });
  });