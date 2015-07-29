angular
  .module('neuralNoise', ['ngMaterial'])
  .controller('MainController', MainController)
  .config(function($mdThemingProvider){
    $mdThemingProvider.theme('default')
      .primaryPalette('blue')
      .accentPalette('green');
  });

function MainController() {
  this.temperature = '';
  this.checkpoint = '';
}

MainController.prototype.getRandomSong = function() {
  window.location = ('/query?checkpoint=' + this.checkpoint + '&temperature=' +
                     this.temperature);
}
