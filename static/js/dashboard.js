document.querySelectorAll('.faq-toggle').forEach(button => {
  button.addEventListener('click', () => {
    // Toggle the active class on the button
    button.classList.toggle('active');
    
    // Get the associated content div
    const content = button.nextElementSibling;
    
    // Toggle the visibility of the content div with smooth animation
    if (content.style.maxHeight) {
      content.style.maxHeight = null; // Close the content
    } else {
      content.style.maxHeight = content.scrollHeight + "px"; // Open the content
    }
    
    // Toggle the icon between plus and minus
    const icon = button.querySelector('i');
    icon.classList.toggle('fa-plus');
    icon.classList.toggle('fa-minus');
  });
});
