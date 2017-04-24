var functions = require('firebase-functions');

const admin = require('firebase-admin');
admin.initializeApp(functions.config().firebase);

// // Create and Deploy Your First Cloud Functions
// // https://firebase.google.com/docs/functions/write-firebase-functions
//
// exports.helloWorld = functions.https.onRequest((request, response) => {
//  response.send("Hello from Firebase!");
// });


exports.createUserInDatabase = functions.auth.user().onCreate(event =>{
	console.log(event.data);
	var email = event.data.email;
	var uid = event.data.uid;

	console.log("Creating user in Database. UID: " + uid);

	var rand_pin = Math.floor( Math.random() * 1000 );
	var pin = ('000' + x).substr(-4);
});