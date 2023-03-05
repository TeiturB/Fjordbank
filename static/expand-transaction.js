$(document).ready(function() {
    // Hide all extra info containers initially
    $('.extra-info-container').hide();
    
    // Add click event listener to each row
    $('tbody tr').click(function() {
        // Get the next row with extra information
        var extraInfoRow = $(this).next('.extra-info-row');
        
        // Toggle the visibility of the extra information container
        extraInfoRow.find('.extra-info-container').slideToggle();
    });
});