package sk.stuba.fiit.vnos.nfcpass.User;

/**
 * Created by jakub on 24.04.2017.
 */

public class UserCache {
    //create an object of SingleObject
    private static UserCache instance = new UserCache();

    private User loggedUser;

    //make the constructor private so that this class cannot be
    //instantiated
    private UserCache(){}

    //Get the only object available
    public static UserCache getInstance(){
        return instance;
    }

    public User getLoggedUser() {
        return loggedUser;
    }

    public void setLoggedUser(User loggedUser) {
        this.loggedUser = loggedUser;
    }
}
