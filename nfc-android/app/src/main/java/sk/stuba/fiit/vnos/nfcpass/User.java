package sk.stuba.fiit.vnos.nfcpass;

import android.content.SharedPreferences;

import com.google.firebase.auth.FirebaseUser;

/**
 * Created by jakub on 24.04.2017.
 */

public class User {
    private String name;
    private String email;
    private String nid;
    private String pin;
    private FirebaseUser firebaseUser;

    public User() {
    }

    public User(String name, String nid, String pin) {
        this.name = name;
        this.nid = nid;
        this.pin = pin;
    }

    public String getName() {
        return name;
    }

    public void setName(String name) {
        this.name = name;
    }

    public String getPin() {
        return pin;
    }

    public void setPin(String pin) {
        this.pin = pin;
    }

    public String getEmail() {
        return email;
    }

    public void setEmail(String email) {
        this.email = email;
    }

    public String getNid() {
        return nid;
    }

    public void setNid(String nid) {
        this.nid = nid;
    }

    public FirebaseUser getFirebaseUser() {
        return firebaseUser;
    }

    public void setFirebaseUser(FirebaseUser firebaseUser) {
        this.firebaseUser = firebaseUser;
    }

    @Override
    public String toString() {
        return "User{" +
                "pin='" + pin + '\'' +
                ", nid='" + nid + '\'' +
                ", email='" + email + '\'' +
                ", name='" + name + '\'' +
                '}';
    }

    public static User loadUser(SharedPreferences sharedPref) {
        User user = new User();
        user.setName(sharedPref.getString("username",null));
        user.setNid(sharedPref.getString("nfcId",null));
        user.setPin(sharedPref.getString("pin",null));
        return user;
    }

    public boolean saveUser(SharedPreferences sharedPref) {
        SharedPreferences.Editor editor = sharedPref.edit();
        editor.putString("username",this.name);
        editor.putString("nfcId",this.nid);
        editor.putString("pin",this.pin);
        return editor.commit();
    }

    public boolean removeUser(SharedPreferences sharedPref) {
        SharedPreferences.Editor editor = sharedPref.edit();
        editor.remove("username");
        editor.remove("nfcId");
        editor.remove("pin");
        return editor.commit();
    }
}
