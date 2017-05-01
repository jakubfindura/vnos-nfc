package sk.stuba.fiit.vnos.nfcpass;

/**
 * Created by jakub on 30.04.2017.
 */

public class Helper {

    public static byte[] concatByteArrays(byte[] arrayA, byte[] arrayB) {
        byte[] arrayC = new byte[arrayA.length + arrayB.length];
        System.arraycopy(arrayA, 0, arrayC, 0, arrayA.length);
        System.arraycopy(arrayB, 0, arrayC, arrayA.length, arrayB.length);
        return arrayC;
    }

    public static byte[] concatByteArrays(byte[]... arrays) {
        byte[] result = new byte[]{};

        for ( byte[] array : arrays ) {
            byte[] tmp = new byte[result.length + array.length];
            System.arraycopy(result, 0, tmp, 0, result.length);
            System.arraycopy(array, 0, tmp, result.length, array.length);
            result = tmp;
        }

        return result;
    }

    /**
     * http://stackoverflow.com/questions/18714616/convert-hex-string-to-byte
     * @param s
     * @return
     */
    public static byte[] hexStringToByteArray(String s) {
        int len = s.length();
        byte[] data = new byte[len/2];

        for(int i = 0; i < len; i+=2){
            data[i/2] = (byte) ((Character.digit(s.charAt(i), 16) << 4) + Character.digit(s.charAt(i+1), 16));
        }

        return data;
    }


    /**
     * http://stackoverflow.com/questions/18714616/convert-hex-string-to-byte
     * @param bytes
     * @return
     */
    final protected static char[] hexArray = {'0','1','2','3','4','5','6','7','8','9','A','B','C','D','E','F'};
    public static String byteArrayToHexString(byte[] bytes, boolean spaced) {
        char[] hexChars = new char[bytes.length*2];
        int v;

        for(int j=0; j < bytes.length; j++) {
            v = bytes[j] & 0xFF;
            hexChars[j*2] = hexArray[v>>>4];
            hexChars[j*2 + 1] = hexArray[v & 0x0F];
        }

        if ( spaced ) {
            return new String(hexChars).replaceAll("(.{2})", "$1 ");
        } else {
            return new String(hexChars);
        }
    }
}
