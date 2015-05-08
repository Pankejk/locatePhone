package com.example.mike.locatephonesystem;

import android.app.Activity;
import android.content.Context;
import android.hardware.Sensor;
import android.hardware.SensorEvent;
import android.hardware.SensorEventListener;
import android.hardware.SensorManager;
import android.net.ConnectivityManager;
import android.net.NetworkInfo;
import android.net.wifi.WifiManager;
import android.os.AsyncTask;
import android.os.Bundle;
import android.support.v7.app.ActionBarActivity;
import android.util.Log;
import android.view.Menu;
import android.view.MenuItem;
import android.widget.Toast;

import org.apache.http.HttpResponse;
import org.apache.http.client.HttpClient;
import org.apache.http.client.methods.HttpPost;
import org.apache.http.entity.StringEntity;
import org.apache.http.impl.client.DefaultHttpClient;
import org.apache.http.params.BasicHttpParams;
import org.apache.http.params.HttpConnectionParams;
import org.apache.http.params.HttpParams;
import org.json.JSONObject;

import java.io.BufferedReader;
import java.io.IOException;
import java.io.InputStream;
import java.io.InputStreamReader;
import java.net.URI;
import java.util.ArrayList;
import java.util.List;


public class MainActivity extends ActionBarActivity implements SensorEventListener {
    private static SensorManager mSensorManager;
    private static Sensor mSensor;
    private static WifiManager wifiManager;
    private static Integer sensorCounter = 0;
    private static String prepare = "";
    private static List <String> magneticList = new ArrayList<String>();
    private static List <Float> magnetList = null;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_main);
        mSensorManager = (SensorManager) getSystemService(Context.SENSOR_SERVICE);
        if (mSensorManager.getDefaultSensor(Sensor.TYPE_MAGNETIC_FIELD) != null){
            // Success! There's a magnetometer.
            String status= "";
            List<Sensor> mmSensor = mSensorManager.getSensorList(Sensor.TYPE_MAGNETIC_FIELD);
            mSensor = mmSensor.get(0);
            Integer size = mmSensor.size();
            Float resolution = mmSensor.get(0).getResolution();
            Float range = mmSensor.get(0).getMaximumRange();
            Float power_req = mmSensor.get(0).getPower();
            Integer minDelay = mmSensor.get(0).getMinDelay();
            String vendor = mmSensor.get(0).getVendor();
            Integer version = mmSensor.get(0).getVersion();
            //Integer maxDelay = gravSensors.get(0).getMaxDelay();
            Log.i("INFO", size.toString());
            Log.i("Resolution: ", resolution.toString());
            Log.i("Range: ", range.toString());
            Log.i("Power Requirement: ", power_req.toString());
            Log.i("Min delay: ", minDelay.toString());
            Log.i("Get vendor: ", vendor);
            Log.i("Get version: ", version.toString());
            //wifi
            //wifiManager = (WifiManager) getSystemService(Context.WIFI_SERVICE);
            //WifiInfo wifiInfo = wifiManager.getConnectionInfo();
            //Integer rssi = wifiInfo.getRssi();
            //Log.i("RSSI: ", rssi.toString());
            //Log.i("RSSI", rssi.toString());
            //status = "\n\nWiFi Status: " + wifiInfo.toString();
            //Log.i("INFO", status);
            //status = "";
            //List<WifiConfiguration> list = wifiManager.getConfiguredNetworks();
            //Integer ile = list.size();
            //Log.i("ile AP: ", ile.toString());
            //for (WifiConfiguration config : list){
            //    Log.i("Lista: ", config.toString());
            //}

            //List<WifiConfiguration> configs = wifiManager.getConfiguredNetworks();
            //for (WifiConfiguration config : configs) {
            //    status = "\n\n" + config.toString();
            //}
            //Log.i("AP: ", status);
            //Log.i("INFO", "PRZED");
            //mSensorManager.registerListener(this, mSensor, SensorManager.SENSOR_DELAY_FASTEST, SensorManager.SENSOR_STATUS_ACCURACY_HIGH);
            //Log.i("INFO", "Za");
            //if (sensorCounter == 100) {
            //    mSensorManager.unregisterListener(this);
           // }
            //magneticList.add("MICHA");
            //magneticList.add("ZAKRZW");
            //ConnectivityManager connMgr = (ConnectivityManager) getSystemService(Activity.CONNECTIVITY_SERVICE);
            //NetworkInfo networkInfo = connMgr.getActiveNetworkInfo();
            //sendData();
            new HttpAsyncTask().execute("http://hmkcode.appspot.com/jsonservlet");

            //Log.i("Max delay: ", maxDelay.toString());
        }
        else {
            // Failure! No magnetometer.
        }
    }

    private class HttpAsyncTask extends AsyncTask<String, Void, String> {
        @Override
        protected String doInBackground(String... urls) {
            mSensorManager.registerListener((SensorEventListener) this, mSensor, SensorManager.SENSOR_DELAY_FASTEST, SensorManager.SENSOR_STATUS_ACCURACY_HIGH);
            while(true){
                if (sensorCounter == 100){
                    //onPause();
                    break;
                }
            }

            return sendData();
        }
        // onPostExecute displays the results of the AsyncTask.
        @Override
        protected void onPostExecute(String result) {
            Toast.makeText(getBaseContext(), "Data Sent!", Toast.LENGTH_LONG).show();
        }
    }

    public String sendData(){
        Log.i("Max delay: ", "Weszło");
        magneticList.add("Michalzxc");
        magneticList.add("Pawel");
        InputStream inputStream = null;
        String result = "";
        try {

            HttpParams httpParameters = new BasicHttpParams();
            int timeoutConnection = 4000;
            HttpConnectionParams.setConnectionTimeout(httpParameters, timeoutConnection);
            int timeoutSocket = 6000;
            HttpConnectionParams.setSoTimeout(httpParameters, timeoutSocket);
            HttpClient httpclient = new DefaultHttpClient(httpParameters);
            URI absolute = new URI("http://192.168.1.26:81/");
            HttpPost httpPost = new HttpPost(absolute);
            String json = "";
            JSONObject jsonObject = new JSONObject();
            Integer counter = 0;
            for (String item : magneticList) {
                jsonObject.accumulate(counter.toString(), item);
                counter++;
            }
            // 4. convert JSONObject to JSON to String
            json = jsonObject.toString();

            // ** Alternative way to convert Person object to JSON string usin Jackson Lib
            // ObjectMapper mapper = new ObjectMapper();
            // json = mapper.writeValueAsString(person);

            // 5. set json to StringEntity
            StringEntity se = new StringEntity(json);
            // 6. set httpPost Entity
            httpPost.setEntity(se);

            // 7. Set some headers to inform server about the type of the content
           // httpPost.setHeader("Accept", "application/json");
            httpPost.setHeader("content-type", "application/json");

            // 8. Execute POST request to the given URL
           // httpclient.getConnectionManager();
            Log.i("INFO",json);
            Log.i("Max delay: ", "Weszło1111");
            isConnected();
            HttpResponse httpResponse = httpclient.execute(httpPost);
            Log.i("INFO", httpResponse.toString());

            // 9. receive response as inputStream
            //inputStream = httpResponse.getEntity().getContent();

            // 10. convert inputstream to string
            /*if (inputStream != null){
                result = convertInputStreamToString(inputStream);
            Log.i("SUCCESS: ", result);
            }else
                result = "Did not work!";*/
            //Log.i("postData", response.getStatusLine().toString());
            //Could do something better with response.
        }catch(Exception e){
            Log.i("InputStream", e.getLocalizedMessage());
        }
        return "";
    }
    private static String convertInputStreamToString(InputStream inputStream) throws IOException {
        BufferedReader bufferedReader = new BufferedReader( new InputStreamReader(inputStream));
        String line = "";
        String result = "";
        while((line = bufferedReader.readLine()) != null)
            result += line;

        inputStream.close();
        return result;

    }

    public boolean isConnected() {
        ConnectivityManager connMgr = (ConnectivityManager) getSystemService(Activity.CONNECTIVITY_SERVICE);
        NetworkInfo networkInfo = connMgr.getActiveNetworkInfo();
        if (networkInfo != null && networkInfo.isConnected()) {
            Log.i("Info", "Jest polaczenie");
            return true;
        }
        else
            return false;
    }

        @Override
    public boolean onCreateOptionsMenu(Menu menu) {
        // Inflate the menu; this adds items to the action bar if it is present.
        getMenuInflater().inflate(R.menu.menu_main, menu);
        return true;
    }

    @Override
    public final void onAccuracyChanged(Sensor sensor, int accuracy) {
        // Do something here if sensor accuracy changes.
    }

    /*public void prepareValues(Float digit){

        prepare = digit.toString() + ":";
        Log.i("Magnetyzm: ", digit.toString());
        if (sensorCounter % 3 == 0 && sensorCounter != 0){
            magneticList.add(prepare);
            prepare="";
        }
        if (sensorCounter == 100) {
            mSensorManager.unregisterListener(this);
            sendData(magneticList);
        }*/
    //}
    @Override
    public final void onSensorChanged(SensorEvent event) {
        // The light sensor returns a single value.
        // Many sensors return 3 values, one for each axis.
        //Float magneticCurrent = event.values[0];
        //Log.i("Magnetyzm: ", magneticCurrent.toString());
        //magnetList.add(event.values[0]);
        //magnetList.add(event.values[1]);
        //magnetList.add(event.values[2]);
        Float tmp = event.values[0];
        Log.i("Magnetyzm: ", tmp.toString());
        magneticList.add(event.toString());
        sensorCounter ++;
        //sendData(magneticCurrent);

        // Do something with this sensor value.
    }

    @Override
    public boolean onOptionsItemSelected(MenuItem item) {
        // Handle action bar item clicks here. The action bar will
        // automatically handle clicks on the Home/Up button, so long
        // as you specify a parent activity in AndroidManifest.xml.
        int id = item.getItemId();

        //noinspection SimplifiableIfStatement
        if (id == R.id.action_settings) {
            return true;
        }

        return super.onOptionsItemSelected(item);
    }

    @Override
    protected void onResume() {
        super.onResume();
        mSensorManager.registerListener(this, mSensor, SensorManager.SENSOR_DELAY_FASTEST,  SensorManager.SENSOR_STATUS_ACCURACY_HIGH);
    }

    @Override
    protected void onPause() {
        super.onPause();
        mSensorManager.unregisterListener(this);
    }
}
