package com.example.mike.locatephonesystem;

import android.app.Activity;
import android.content.Context;
import android.content.Intent;
import android.hardware.Sensor;
import android.hardware.SensorEvent;
import android.hardware.SensorEventListener;
import android.hardware.SensorManager;
import android.net.ConnectivityManager;
import android.net.NetworkInfo;
import android.net.wifi.ScanResult;
import android.net.wifi.WifiManager;
import android.os.AsyncTask;
import android.os.Bundle;
import android.support.v7.app.ActionBarActivity;
import android.util.Log;
import android.view.Menu;
import android.view.MenuItem;
import android.view.View;
import android.widget.Button;
import android.widget.EditText;
import android.widget.TextView;
import android.widget.Toast;

import org.apache.http.HttpResponse;
import org.apache.http.client.HttpClient;
import org.apache.http.client.methods.HttpPost;
import org.apache.http.entity.StringEntity;
import org.apache.http.impl.client.DefaultHttpClient;
import org.apache.http.params.BasicHttpParams;
import org.apache.http.params.HttpConnectionParams;
import org.apache.http.params.HttpParams;
import org.json.JSONException;
import org.json.JSONObject;

import java.io.BufferedReader;
import java.io.IOException;
import java.io.InputStream;
import java.io.InputStreamReader;
import java.io.UnsupportedEncodingException;
import java.net.URI;
import java.util.ArrayList;
import java.util.List;


public class MainActivity extends ActionBarActivity implements SensorEventListener, View.OnClickListener {
    private static SensorManager mSensorManager;
    private static Sensor mSensor;
    private static WifiManager wifiManager;
    private static Integer sensorCounter = 0;
    private static Integer wifiCounter = 0;
    private static List <Float> magneticList = new ArrayList<Float>();
    private static List<List<ScanResult>> wifiSeen = new ArrayList<List<ScanResult>>();
    private static List<String> magneticJson = new ArrayList<String>();
    private static List<String> rssiJson = new ArrayList<String>();
    //private static List<String> locationMagneticJson = new ArrayList<String>();
    //private static List<String> locationRssiJson = new ArrayList<String>();
    List<StringEntity> entityMagnetic = new ArrayList<>();
    List<StringEntity> entityRssi = new ArrayList<>();
    private static Float x = Float.valueOf(0);
    private static Float y = Float.valueOf(0);
    private static String place_name = "DEFAULT";

    private static TextView textView;
    private static EditText editText;

    private static GainData dataCollector;



    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_main);
        Button button = (Button) findViewById(R.id.button);
        button.setOnClickListener(this);
        Button button2 = (Button) findViewById(R.id.button2);
        button2.setOnClickListener(this);
        Button button3 = (Button) findViewById(R.id.button3);
        button3.setOnClickListener(this);
        Button button4 = (Button) findViewById(R.id.button4);
        button4.setOnClickListener(this);
        Button button5 = (Button) findViewById(R.id.button4);
        button5.setOnClickListener(this);
        textView = (TextView) findViewById(R.id.textView);
        editText = (EditText) findViewById(R.id.editText);

        //mSensorManager = (SensorManager) getSystemService(Context.SENSOR_SERVICE);
        //wifiManager = (WifiManager) getSystemService(Context.WIFI_SERVICE);
        /*for (ScanResult item : wifiSeen){
            Log.i("Info" , item.toString());
        }*/

        //dataCollector = new GainData(this);
       // if (mSensorManager.getDefaultSensor(Sensor.TYPE_MAGNETIC_FIELD) != null){
            // Success! There's a magnetometer.
           /* String status= "";
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
            Log.i("Get version: ", version.toString());*/
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
            //new HttpAsyncTask().execute("http://hmkcode.appspot.com/jsonservlet");

            //Log.i("Max delay: ", maxDelay.toString());
       // }
        //else {
            // Failure! No magnetometer.
       // }
    }

    public void onClick(View v) {
        switch (v.getId()) {
            case  R.id.button: {
                Intent intent = new Intent(this, GainData.class);
                intent.putExtra(GainData.X_INTENT,x);
                intent.putExtra(GainData.Y_INTENT,y);
                intent.putExtra(GainData.PLACE_NAME_INTENT,place_name);

                startService(intent);
                //dataCollector.startGainData(x,y, place_name);
                /*magneticList.clear();
                wifiSeen.clear();
                textView.clearComposingText();
                List<Sensor> mmSensor = mSensorManager.getSensorList(Sensor.TYPE_MAGNETIC_FIELD);
                mSensor = mmSensor.get(0);
                mSensorManager.registerListener((SensorEventListener) this, mSensor, SensorManager.SENSOR_DELAY_FASTEST, SensorManager.SENSOR_STATUS_ACCURACY_HIGH);

                wifiCounter = 0;
                sensorCounter = 0;
                Log.i("INFO", "ZBIERANIE DANYCH");
                while (true) {
                    wifiManager.startScan();
                    Log.i("INFO",wifiManager.getScanResults().get(0).getClass().toString());
                    wifiSeen.add(wifiManager.getScanResults());
                    //wifiSeen.get(0).
                    wifiCounter ++;
                    if (wifiCounter == 20) {
                        textView.setText("WIFI z pozycji jest juz sciagniete\n");
                        break;
                    }

                    Log.i("INFO", "Parsowanie danych");
                    try {
                        prepareJson(x, y, 1);
                    } catch (JSONException e) {
                        e.printStackTrace();
                    }
                }*/
                break;
                //new HttpAsyncTask().execute("http://hmkcode.appspot.com/jsonservlet");
                // do something for button 1 click
            }

            case R.id.button2: {
                // do something for button 2 click
                //preapreStringEntity();
                //sendData();//new HttpAsyncTask().execute("http://hmkcode.appspot.com/jsonservlet");//sendData();
                //entityRssi = dataCollector.getMagneticEntityList();
                //entityMagnetic = dataCollector.getRssiEntityList();
                //new HttpAsyncTask().execute("http://hmkcode.appspot.com/jsonservlet");
                break;
            }

            case R.id.button3:{
                x +=1;
                break;
            }
            case R.id.button4:{
                y +=2;
                break;
            }
            case R.id.button5:{
                this.place_name=editText.getText().toString();
                break;
            }
        }
    }

    private class HttpAsyncTask extends AsyncTask<String, Void, String> {
        @Override
        protected String doInBackground(String... urls) {
            //List<Sensor> mmSensor = mSensorManager.getSensorList(Sensor.TYPE_MAGNETIC_FIELD);
           // mSensor = mmSensor.get(0);
            //mSensorManager.registerListener((SensorEventListener) this, mSensor, SensorManager.SENSOR_DELAY_FASTEST, SensorManager.SENSOR_STATUS_ACCURACY_HIGH);
           // while(true){
           //     if (sensorCounter == 100){
                    //mSensorManager.unregisterListener((SensorEventListener) this);//onPause();
            //        break;
            //    }
           // }


            sendData();
            return "";
        }
        // onPostExecute displays the results of the AsyncTask.
        @Override
        protected void onPostExecute(String result) {
            Toast.makeText(getBaseContext(), "Data Sent!", Toast.LENGTH_LONG).show();
        }
    }

    public void prepareJson(Float x, Float y, Integer choice) throws JSONException {
        JSONObject jsonObject = new JSONObject();
        String tmp ="";
        if (choice == 0) {
            for (Float item : magneticList) {
                    tmp += item.toString() + "%";

            }

        } else if (choice == 1){
            for (List<ScanResult> item : wifiSeen) {
                for (ScanResult record : item){
                    tmp += item.toString() + "%";
                    }
                }
        }


        jsonObject.accumulate("x", x);
        jsonObject.accumulate("y", y);
        jsonObject.accumulate("data", tmp);
        if (choice == 0){
            magneticJson.add(jsonObject.toString());
        } else if (choice == 1){
            rssiJson.add(jsonObject.toString());

        }
        Log.i("INFO", "JSONY GOTOWE");

    }
/*
    public void preapreStringEntity(){

        try {
            for(String item : magneticJson){
                Log.i("Max delay: ", "!!!!!!!!!!!!!!!!!!!!!!!!!!!");
                magneticEntity.add(new StringEntity(item));
            }
            for(String item : rssiJson){
            Log.i("Max delay: ", "?????????????????????????????");
                rssiEntity.add(new StringEntity(item));
            }
        } catch (UnsupportedEncodingException e) {
            e.printStackTrace();
        }
        Log.i("Max delay: ", "String entity gotowe");
    }*/

    public StringEntity prepareStringEntity(String tmp){

        StringEntity en = null;
        try {
            Log.i("INFO", tmp);
            en = new StringEntity(tmp);
        } catch (UnsupportedEncodingException e) {
            e.printStackTrace();
        }

        return en;

    }

    public String sendData(){
        Log.i("MAIN ACTIVITY ", "Weszło");
        //magneticList.add("Michalzxc");
        //magneticList.add("Pawel");
        InputStream inputStream = null;
        String result = "";
        try {

            HttpParams httpParameters = new BasicHttpParams();
            int timeoutConnection = 4000;
            Log.i("MAIN ACTIVITY: ", "11111111111");
            HttpConnectionParams.setConnectionTimeout(httpParameters, timeoutConnection);
            int timeoutSocket = 6000;
            Log.i("MAIN ACTIVITY: ", "2222222222222222");
            HttpConnectionParams.setSoTimeout(httpParameters, timeoutSocket);
            Log.i("MAIN ACTIVITY: ", "3333333333333333333");
            HttpClient httpclient = new DefaultHttpClient();
            URI absolute = new URI("http://192.168.1.31:8080");
            Log.i("MAIN ACTIVITY: ", "44444444444444444444444");
            //String json = "";
            /*JSONObject jsonObject = new JSONObject();
            for (String item : magneticList) {
                jsonObject.accumulate(counter.toString(), item);
            }*/
            // 4. convert JSONObject to JSON to String
            //json = prepareJson();

            // ** Alternative way to convert Person object to JSON string usin Jackson Lib
            // ObjectMapper mapper = new ObjectMapper();
            // json = mapper.writeValueAsString(person);

            // 5. set json to StringEntity

            /*Log.i("MAIN ACTIVITY: ", "5555555555555555555555555555");
            //StringEntity se = new StringEntity(json);
            // 6. set httpPost Entity
            for (String se : magneticJson){
                HttpPost httpPost = new HttpPost(absolute);
                httpPost.setEntity(prepareStringEntity(se));
                httpPost.setHeader("Accept", "application/json");
                httpPost.setHeader("content-type", "application/json");
                Log.i("MAIN ACTIVITY: ", "66666666666666666666");
                if (isConnected()){
                    Log.i("CONTENT",se);
                    HttpResponse httpResponse = httpclient.execute(httpPost);
                    Log.i("MAIN ACTIVITY: ", "777777777777777777777777  ");
                    Log.i("INFO", httpResponse.toString());
                }


                magneticJson.clear();
                rssiJson.clear();
            }

            for (String se : rssiJson) {
                HttpPost httpPost = new HttpPost(absolute);
                httpPost.setEntity(prepareStringEntity(se));
                httpPost.setHeader("Accept", "application/json");
                httpPost.setHeader("content-type", "application/json");
                Log.i("MAIN ACTIVITY: ", "8888888888888");
                if (isConnected()) {
                    HttpResponse httpResponse = httpclient.execute(httpPost);
                    Log.i("MAIN ACTIVITY: ", "999999999999999999999  ");
                    Log.i("INFO", httpResponse.toString());
                }
            }*/
            HttpPost httpPost = new HttpPost(absolute);
            Log.i("MAIN ACTIVITY: ", "66666666666666666666");
            httpPost.setEntity(entityMagnetic.get(0));
            for (StringEntity en : entityRssi){
                httpPost.setEntity(en);
            }

            Log.i("MAIN ACTIVITY: ", "7777777777777777777777777777");
            httpPost.setHeader("Accept", "application/json");
            Log.i("MAIN ACTIVITY: ", "888888888888888888888");
            httpPost.setHeader("content-type", "application/json");
            //Log.i("POST:" , prepareStringEntity(rssiJson.get(0)).getContent().toString());
            Log.i("MAIN ACTIVITY: ", "999999999999999999999");
            if (isConnected()){
                //Log.i("CONTENT",se);
                Log.i("MAIN ACTIVITY: ", "YYYYYYYYYYYYYYYYYYYY");
                try {
                    HttpResponse httpResponse = httpclient.execute(httpPost);
                    Log.i("MAIN ACTIVITY: ", httpResponse.toString());
                }catch(Exception ex){
                    ex.printStackTrace();
                }
                Log.i("MAIN ACTIVITY: ", "rrrrrrrrrrrrrrrrrrrr  ");
               // Log.i("INFO", httpResponse.toString());
            }


            // 7. Set some headers to inform server about the type of the content
           // httpPost.setHeader("Accept", "application/json");
            //httpPost.setHeader("content-type", "application/json");

            // 8. Execute POST request to the given URL
           // httpclient.getConnectionManager();
            //Log.i("INFO",json);
           // Log.i("MAIN ACTIVITY: ", "Weszło1111");
            //if (isConnected()) {
            //    HttpResponse httpResponse = httpclient.execute(httpPost);
            //    Log.i("INFO", httpResponse.toString());
            //}

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
            Log.i("InputStream", "przejebka");
            e.printStackTrace();
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
      //  if (mSensorManager.getDefaultSensor(Sensor.TYPE_MAGNETIC_FIELD) != null) {
            List<Float> tmp = new ArrayList<Float>();
            tmp.add(event.values[0]);
            tmp.add(event.values[1]);
            tmp.add(event.values[2]);
            Log.i("Magnetyzm x : ", tmp.get(0).toString());
            Log.i("Magnetyzm y : ", tmp.get(1).toString());
            Log.i("Magnetyzm z : ", tmp.get(2).toString());
            magneticList.add(tmp.get(0));
            magneticList.add(tmp.get(1));
            magneticList.add(tmp.get(2));
            sensorCounter++;
            stopMagnetometer();
        //}
        //sendData(magneticCurrent);

        // Do something with this sensor value.
    }

    public void stopMagnetometer(){
        if (sensorCounter == 20) {
           // mSensorManager.unregisterListener(this);
            //mSensor=null;
            Integer size = magneticList.size();
            textView.setText("Pole magnetyczne z pozycji jest juz sciagniete\n");
            Log.i("INFO", size.toString());
            try {
                prepareJson(x, y, 0);
            } catch (JSONException e) {
                e.printStackTrace();
            }
        }
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
        //mSensorManager.registerListener(this, mSensor, SensorManager.SENSOR_DELAY_FASTEST,  SensorManager.SENSOR_STATUS_ACCURACY_HIGH);
    }

    @Override
    protected void onPause() {
        super.onPause();
       // mSensorManager.unregisterListener(this);
    }
}
