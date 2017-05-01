package sk.stuba.fiit.vnos.nfcpass.NfcService;

import android.content.Context;
import android.content.SharedPreferences;
import android.nfc.cardemulation.HostApduService;
import android.os.Bundle;
import android.util.Log;
import android.widget.Toast;

import java.nio.ByteBuffer;
import java.text.ParseException;
import java.text.SimpleDateFormat;
import java.util.Date;

import sk.stuba.fiit.vnos.nfcpass.Helper;
import sk.stuba.fiit.vnos.nfcpass.NoUserLoggedException;
import sk.stuba.fiit.vnos.nfcpass.User.User;

/**
 * Created by jakub on 30.04.2017.
 */

public class VnosNfcApduService extends HostApduService {

    private static final String TAG = "VNOS APDU SERVICE";

    private static final byte[] MSG_OK = new byte[] {(byte)0x90, (byte)0x00 };
    private static final byte[] MSG_NO_USER = new byte[] {(byte)0x90, (byte)0x00 };
    private static final byte[] MSG_NOT_SUPPORTED = new byte[] {(byte)0x90, (byte)0x00 };

    private static final byte[] MSG_START = new byte[] {(byte)0xAA, (byte)0xAA };
    private static final byte[] MSG_END = new byte[] {(byte)0x55, (byte)0x55 };

    @Override
    public byte[] processCommandApdu(byte[] commandApdu, Bundle extras) {
        if ( selectAidApdu(commandApdu) ) {
            // App selected, return OK
            Log.v(TAG, "APDU: => " + Helper.byteArrayToHexString(commandApdu,true));
            Log.i(TAG, "APDU: Select AID - Application selected, OK sent");

            Log.v(TAG, "APDU: <= " + Helper.byteArrayToHexString(MSG_OK,true));
            return MSG_OK;
        }

        if ( validMessage(commandApdu)) {
            if ( authRequestApdu(commandApdu) ) {
                Log.v(TAG, "APDU: => " + Helper.byteArrayToHexString(commandApdu,true));
                Log.i(TAG, "APDU: Get Auth Msg - Auth Message Request");

                byte[] response = null;

                try {
                    response = getAuthMessage();
                } catch (NoUserLoggedException e) {
                    Log.e(TAG, "No user logged in application");
                    Toast.makeText(this, "No user logged in NFC Pass", Toast.LENGTH_SHORT).show();
                    response = MSG_NO_USER;
                }

                Log.v(TAG, "APDU: <= " + Helper.byteArrayToHexString(response, true));
                return response;
            }

            if ( authReceivedApdu(commandApdu) ) {
                Log.v(TAG, "APDU: => " + Helper.byteArrayToHexString(commandApdu,true));
                Log.i(TAG, "APDU: Auth OK - Auth Message Received by Device");
                Toast.makeText(this, "Auth message sent through NFC.", Toast.LENGTH_SHORT).show();
                Log.v(TAG, "APDU: <= " + Helper.byteArrayToHexString(MSG_OK,true));
                return MSG_OK;
            }
        }

        Log.v(TAG, "APDU: <= " + Helper.byteArrayToHexString(MSG_NOT_SUPPORTED,true));
        return MSG_NOT_SUPPORTED;
    }

    private boolean validMessage(byte[] apdu) {
        if( apdu[0] != (byte)0xAA && apdu[1] != (byte)0xAA  )
            return false;
        if( apdu[apdu.length-1] != (byte)0x55 && apdu[apdu.length-2] != (byte)0x55)
            return false;

        return true;
    }

    private boolean authReceivedApdu(byte[] apdu) {
        return ( apdu[2] == (byte)0x03 );
    }

    private boolean authRequestApdu(byte[] apdu) {
        return ( apdu[2] == (byte)0x02 );
    }

    @Override
    public void onDeactivated(int reason) {
        Log.i(TAG,"VnosNfcApduService deactivated: " + reason);
    }

    private boolean selectAidApdu(byte[] apdu) {
        return apdu.length >= 2 && apdu[0] == (byte)0 && apdu[1] == (byte)0xa4;
    }

    private byte[] getAuthMessage() throws NoUserLoggedException {
        SharedPreferences sharedPrefs = this.getSharedPreferences("nfc_user_prefs", Context.MODE_PRIVATE);
        User user = User.loadUser(sharedPrefs);
        if ( user.getNid() == null ) {
            throw new NoUserLoggedException();
        }

        Log.d(TAG, "NFC ID: " + user.getNid());
        byte[] id = Helper.hexStringToByteArray(user.getNid());

        SimpleDateFormat sdf = new SimpleDateFormat("yyyy-MM-dd HH");
        Date date = null;
        try {
            date = sdf.parse(sdf.format(new Date()));
        } catch (ParseException e) {
            e.printStackTrace();
        }

        byte[] ts = ByteBuffer.allocate(Integer.SIZE / Byte.SIZE).putInt((int) (date.getTime()/1000)).array();

        byte[] msg = Helper.concatByteArrays(MSG_START, new byte[]{(byte)0x10}, id, ts, MSG_END);
        Log.d(TAG, "Auth message: " + Helper.byteArrayToHexString(msg,true));
        return msg;
    }

}
