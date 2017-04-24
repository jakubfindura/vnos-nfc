var functions = require('firebase-functions');
const admin = require('firebase-admin');
const md5 = require('md5');

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
	var name = event.data.displayName;
	var uid = event.data.uid;

	console.log("Creating user in Database. UID: " + uid);

	var rand_pin = Math.floor( Math.random() * 1000 );
	var pin = ('000' + rand_pin).substr(-4);

	var nfc_id = generateNFCId(uid);

	console.log("Saving new user: " + name);
	console.log("User parameters: NFCID: " + nfc_id + ", PIN: " + pin);
	admin.database().ref('/users').child(uid).set({
		name: name,
		email: email,
		pin: pin,
		nid: nfc_id
	}).then(function(){
		console.log("New user saved to Database.");
	}).catch(function(){
		console.log("Failed to save user to Database!");
	});

});

function generateNFCId(uid) {
	var nid = md5(uid);
	return nid;
	// Generates ID for NFC
	// Length of ID is 16 bytes
	// Example: a1b2c3d4e5f6a7b8
}