$(document).ready(function() {
    var totalSteps = $('.step').length;
    var currentStep = 1;
    
    function updateStepIndicator() {
      $('#currentStep').text(currentStep);
      $('#totalSteps').text(totalSteps);
    }
  
    $('.next').click(function() {
      if (currentStep < totalSteps) {
        $('#step' + currentStep).removeClass('active');
        currentStep++;
        $('#step' + currentStep).addClass('active');
        updateStepIndicator();
      }
    });
  
    $('.prev').click(function() {
      if (currentStep > 1) {
        $('#step' + currentStep).removeClass('active');
        currentStep--;
        $('#step' + currentStep).addClass('active');
        updateStepIndicator();
      }
    });
  
    // Rest of your code for form submission
  });

 