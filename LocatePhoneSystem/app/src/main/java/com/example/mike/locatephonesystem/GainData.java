package com.example.mike.locatephonesystem;

import android.app.Activity;
import android.app.Service;
import android.content.Context;
import android.content.Intent;
import android.hardware.Sensor;
import android.hardware.SensorEvent;
import android.hardware.SensorEventListener;
import android.hardware.SensorManager;
import android.net.ConnectivityManager;
import android.net.NetworkInfo;
import android.net.wifi.ScanResult;
import android.net.wifi.WifiInfo;
import android.net.wifi.WifiManager;
import android.os.AsyncTask;
import android.os.IBinder;
import android.util.ArrayMap;
import android.util.Log;
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

import java.io.UnsupportedEncodingException;
import java.net.URI;
import java.text.SimpleDateFormat;
import java.util.ArrayList;
import java.util.Date;
import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.Set;

/**
 * Created by mike on 6/15/15.
 */
public class GainData extends Service implements SensorEventListener {

    private static Context context;
    private static WifiManager wifiManager;
    private static SensorManager mSensorManager;
    private static Sensor mSensor;


    //INTENT COMMUNICATION
    public static final String X_INTENT = "X";
    public static final String Y_INTENT = "Y";
    public static final String PLACE_NAME_INTENT ="PLACE_NAME";
    private static final Integer DATA_SIZE = 20;
    private static final Integer MAGNETIC_CHOICE = 0;
    private static final Integer RSSI_CHOICE = 1;
    private static final Map<String,String> CONSTANT_MAGNETIC_JSON = new HashMap();
    static{
        //static fileds in json files
        Map<String, String> aMap = new HashMap<>();
        aMap.put("PLACE","PLACE");
        aMap.put("POSITIONS","POSITIONS");
        aMap.put("TIMESTAMP","TIMESTAMP");
        aMap.put("MAGNETIC_DATA","MAGNETIC_DATA");
        aMap.put("MAGNETIC_AVG_TIME","MAGNETIC_AVG_TIME");
        aMap.put("IP_PHONE","IP_PHONE");
        aMap.put("MAC_PHONE","MAC_PHONE");

        aMap.put("SSID","SSID");
        aMap.put("MAC_AP","MAC_AP");
        aMap.put("RSSI_DATA","RSSI_DATA");
        aMap.put("RSSI_AVG_TIME","RSSI_AVG_TIME");
    };

    private List<JSONObject> jsonMagnetic;
    private List<JSONObject> jsonRssi;
    private Map<String,String> mapMagneticShema = new HashMap();
    private Map<String,String> mapRssiShema = new HashMap();
    private List<StringEntity> entityRssi;
    //private List<List<Float>> rawDataMagnetic = new ArrayList();
    //private List<List<Integer>> rawDataRssi = new ArrayList();
    private List<Float> magneticList = new ArrayList<>();
    private List<List<ScanResult>> apInfoList = new ArrayList();
    private List<List<Long>> timeList = new ArrayList<>();
    private List<Map<String, Float>> avgTimeList = new ArrayList();


    private String place_name="DEFAULT";
    private Float x = Float.valueOf(0);
    private Float y = Float.valueOf(0);
    private Integer phone_ip=0;
    private String phone_mac="";

    private Integer printCounter = 0;
    private Integer magneticCounter = 0;
    private Integer apInfoCounter = 0;
    private Long startTime = Long.valueOf(0);

    @Override
    public void onCreate() {
        // The service is being created
        this.context = getBaseContext();  //getApplicationContext();
        //this.textView = null;// (TextView) findViewById(R.id.textView);
        this.wifiManager = (WifiManager) context.getSystemService(context.WIFI_SERVICE);;
        this.mSensorManager = (SensorManager) context.getSystemService(context.SENSOR_SERVICE);
        List<Sensor> mmSensor = mSensorManager.getSensorList(Sensor.TYPE_MAGNETIC_FIELD);
        this.mSensor = mmSensor.get(0);
        //this.place_name = "DEFAULT";
        this.timeList.add(new ArrayList<Long>());
        this.timeList.add(new ArrayList<Long>());
        this.gainPhoneInfo();
        this.setJsonShema();
    }
    @Override
    public int onStartCommand(Intent intent, int flags, int startId) {
        // The service is starting, due to a call to startService()
        x =intent.getFloatExtra(X_INTENT, 0);
        y =intent.getFloatExtra(Y_INTENT, 0);
        place_name = intent.getStringExtra(PLACE_NAME_INTENT);

        String msg = "x: "  + x.toString() + "y:" + y.toString() + " PLACE NAME: " + place_name;
        printStep(msg);

        startMagnetometer();
        gainRssi();
        measureTimes();
        prepareJson();
        preapreStringEntity();
        sendData();
        //resetTables();
        return 0;
    }


    @Override
    public IBinder onBind(Intent intent) {
        // A client is binding to the service with bindService()
        return null;
    }

   /*public GainData(Context context, TextView textView){

       super();
        this.context = context;
        this.textView = textView;
        this.wifiManager = (WifiManager) context.getSystemService(context.WIFI_SERVICE);;
        this.mSensorManager = (SensorManager) context.getSystemService(context.SENSOR_SERVICE);
        List<Sensor> mmSensor = mSensorManager.getSensorList(Sensor.TYPE_MAGNETIC_FIELD);
        this.mSensor = mmSensor.get(0);
        this.place_name = "DEFAULT";
        this.timeList.add(new ArrayList<Long>());
        this.timeList.add(new ArrayList<Long>());
        this.gainPhoneInfo();
        this.setJsonShema();
    }*/



    public void setPlace(String place_name){
        this.place_name = place_name;
    }

    public List<JSONObject> getMagneticJsonList() {
        return this.jsonMagnetic;
    }

    public List<JSONObject> getRssiJsonList() {
        return this.jsonRssi;
    }

    /*public List<StringEntity> getMagneticEntityList() {
        return this.entityMagnetic;
    }*/

    public List<StringEntity> getRssiEntityList() {
        return this.entityRssi;
    }

    public void resetTables(){
        try {
            this.jsonMagnetic.clear();
            this.jsonRssi.clear();
            //this.entityMagnetic.clear();
            this.entityRssi.clear();
            //this.rawDataMagnetic.clear();
            //this.rawDataRssi.clear();
            this.magneticList.clear();
            this.apInfoList.clear();
            this.timeList.clear();
            this.avgTimeList.clear();
            this.printCounter = 0;
            this.magneticCounter = 0;
            this.apInfoCounter = 0;
        }catch(Exception e){
            Log.i("GAIN DATA " , "SOME LIST MAY BE EMPTY YET");
        }
    }



    private void setJsonShema(){

        //prepare magnetic json shema
        this.mapMagneticShema.put(CONSTANT_MAGNETIC_JSON.get("PLACE"),"");
        this.mapMagneticShema.put(CONSTANT_MAGNETIC_JSON.get("POSITIONS"),"");
        this.mapMagneticShema.put(CONSTANT_MAGNETIC_JSON.get("TIMESTAMP"),"");
        this.mapMagneticShema.put(CONSTANT_MAGNETIC_JSON.get("MAGNETIC_DATA"),"");
        this.mapMagneticShema.put(CONSTANT_MAGNETIC_JSON.get("MAGNETIC_AVG_TIME"),"");
        this.mapMagneticShema.put(CONSTANT_MAGNETIC_JSON.get("IP_PHONE"),"");
        this.mapMagneticShema.put(CONSTANT_MAGNETIC_JSON.get("MAC_PHONE"),"");

        //prepare magnetic json shema
        this.mapRssiShema.put(CONSTANT_MAGNETIC_JSON.get("SSID"),"");
        this.mapRssiShema.put(CONSTANT_MAGNETIC_JSON.get("MAC_AP"), "");
        this.mapRssiShema.put(CONSTANT_MAGNETIC_JSON.get("PLACE"), "");
        this.mapRssiShema.put(CONSTANT_MAGNETIC_JSON.get("POSITIONS"),"");
        this.mapRssiShema.put(CONSTANT_MAGNETIC_JSON.get("TIMESTAMP"), "");
        this.mapRssiShema.put(CONSTANT_MAGNETIC_JSON.get("RSSI_DATA"), "");
        this.mapRssiShema.put(CONSTANT_MAGNETIC_JSON.get("RSSI_AVG_TIME"), "");
        this.mapRssiShema.put(CONSTANT_MAGNETIC_JSON.get("IP_PHONE"), "");
        this.mapRssiShema.put(CONSTANT_MAGNETIC_JSON.get("MAC_PHONE"), "");
    }

    /*public void startGainData(Float x, Float y, String place_name) {
        this.x=x;
        this.y=y;
        this.place_name = place_name;
        startMagnetometer();
        gainRssi();
        measureTimes();
        prepareJson();
        preapreStringEntity();
        sendData();
    }*/


    private void prepareJson() {
        Map<String, String> dataMagneticDict = new HashMap<>();
        List<Map<String, String>> dataRssiDict = new ArrayList<>();
        List<Set> dataRssiSet = new ArrayList<>();


        //preaprsing array amp for createing jsonobejct
        this.feedHashMap(dataMagneticDict, dataRssiDict);

        JSONObject jsonMagneticObject = new JSONObject();



        //prepare json MAGNETIC
        try {
            Log.i("CONSTANT_MAGNETIC_JSON", CONSTANT_MAGNETIC_JSON.get("PLACE"));
            Log.i("dataMagneticDict", dataMagneticDict.get("PLACE"));
            jsonMagneticObject.accumulate(CONSTANT_MAGNETIC_JSON.get("PLACE"),dataMagneticDict.get("PLACE"));
            jsonMagneticObject.accumulate(CONSTANT_MAGNETIC_JSON.get("POSITIONS"),dataMagneticDict.get("POSITIONS"));
            jsonMagneticObject.accumulate(CONSTANT_MAGNETIC_JSON.get("TIMESTAMP"),dataMagneticDict.get("TIMESTAMP"));
            jsonMagneticObject.accumulate(CONSTANT_MAGNETIC_JSON.get("MAGNETIC_DATA"),dataMagneticDict.get("MAGNETIC_DATA"));
            jsonMagneticObject.accumulate(CONSTANT_MAGNETIC_JSON.get("MAGNETIC_AVG_TIME"),dataMagneticDict.get("MAGNETIC_AVG_TIME"));
            jsonMagneticObject.accumulate(CONSTANT_MAGNETIC_JSON.get("IP_PHONE"),dataMagneticDict.get("IP_PHONE"));
            jsonMagneticObject.accumulate(CONSTANT_MAGNETIC_JSON.get("MAC_PHONE"),dataMagneticDict.get("MAC_PHONE"));
            jsonMagnetic.add(jsonMagneticObject);
        } catch (JSONException e) {
            e.printStackTrace();
        }

        //CREATE JSON FOR ALL AP
        try {
            for (Map<String,String> tmpMap : dataRssiDict ){
                JSONObject tmpJsonObject = new JSONObject();
                tmpJsonObject.accumulate(CONSTANT_MAGNETIC_JSON.get("MAC_AP"),tmpMap.get("MAC_AP"));
                tmpJsonObject.accumulate(CONSTANT_MAGNETIC_JSON.get("SSID"),tmpMap.get("SSID"));
                tmpJsonObject.accumulate(CONSTANT_MAGNETIC_JSON.get("PLACE"),tmpMap.get("PLACE"));
                tmpJsonObject.accumulate(CONSTANT_MAGNETIC_JSON.get("POSITIONS"),tmpMap.get("POSITIONS"));
                tmpJsonObject.accumulate(CONSTANT_MAGNETIC_JSON.get("TIMESTAMP"),tmpMap.get("TIMESTAMP"));
                tmpJsonObject.accumulate(CONSTANT_MAGNETIC_JSON.get("RSSI_DATA"),tmpMap.get("RSSI_DATA"));
                tmpJsonObject.accumulate(CONSTANT_MAGNETIC_JSON.get("RSSI_AVG_TIME"),tmpMap.get("RSSI_AVG_TIME"));
                tmpJsonObject.accumulate(CONSTANT_MAGNETIC_JSON.get("IP_PHONE"),tmpMap.get("IP_PHONE"));
                tmpJsonObject.accumulate(CONSTANT_MAGNETIC_JSON.get("MAC_PHONE"),tmpMap.get("MAC_PHONE"));
                jsonRssi.add(tmpJsonObject);
            }
        } catch (JSONException e) {
            e.printStackTrace();
        }

    }

    //function feed Hash Map with data from measurement
    private void feedHashMap(Map<String,String> mapMagnetic, List<Map<String,String>> mapRssi){

        //MAGNETIC MAP
        mapMagnetic.put(CONSTANT_MAGNETIC_JSON.get("PLACE"),place_name);
        mapMagnetic.put(CONSTANT_MAGNETIC_JSON.get("POSITIONS"),changePositonsToString());
        mapMagnetic.put(CONSTANT_MAGNETIC_JSON.get("TIMESTAMP"),timeStamp());
        mapMagnetic.put(CONSTANT_MAGNETIC_JSON.get("MAGNETIC_DATA"),magneticDataToString());
        mapMagnetic.put(CONSTANT_MAGNETIC_JSON.get("MAGNETIC_AVG_TIME"), timeToString(MAGNETIC_CHOICE));
        mapMagnetic.put(CONSTANT_MAGNETIC_JSON.get("IP_PHONE"),phone_ip.toString());
        mapMagnetic.put(CONSTANT_MAGNETIC_JSON.get("MAC_PHONE"), phone_mac);

        //RSSI MAP
        prepareRssiMaps(mapRssi);

        //Log.i("GAIN DATA - magneticarray", mapMagnetic.get("POSITIONS"));
        Log.i("mapMagnetic", mapMagnetic.toString());
        Log.i("mapRssi", mapRssi.toString());
    }

    private String changePositonsToString(){

        String tmp = "{ x:"+ x.toString() + ",y:" + y.toString() +"}";
        return tmp;

    }

    private String timeStamp(){
        Date myDate = new Date();
        SimpleDateFormat sdf = new SimpleDateFormat("yyyy-MM-dd:HH-mm-ss.S");
        String myDateString = sdf.format(myDate);

        return myDateString;
    }

    private String magneticDataToString(){
        String tmp = "[";
        Float data = Float.valueOf(0);
        for (Integer i=0;i<magneticList.size(); i++){
            if (i != magneticList.size()-1){
                data = magneticList.get(i);
                tmp += data.toString() + ",";
            } else{
                data = magneticList.get(i);
                tmp += data.toString();
            }

        }
        Log.i("GAIN DATA:", tmp);
        tmp += "]";

        return tmp;
    }

    private String timeToString(Integer choice){

        return timeList.get(choice).toString();
    }

    private void prepareRssiMaps(List<Map<String,String>> list){

        //printStep("CREATE JSON FOR ALL AP + MAGNETIC JSON");
        //TAKE UNIQUE BSSID
        Map<String,List<Integer>> apDataInteger = new HashMap<>();
        Map<String, Map<String,String>> apDataString = new HashMap<>();
        List<String> uniqueApBSSID = new ArrayList<>();

        for (List<ScanResult> dataList : apInfoList) {
            for (ScanResult result : dataList) {
               if(!uniqueApBSSID.contains(result.BSSID) ){
                   uniqueApBSSID.add(result.BSSID);
                   apDataInteger.put(result.BSSID,new ArrayList<Integer>());
               }
            }
        }

        //ADD ALL LEVELS TO CERTAIN AP
        for (Integer i=0; i<apInfoList.size(); i++ ) {
            for (ScanResult result : apInfoList.get(i)) {
                if(uniqueApBSSID.contains(result.BSSID) ){
                    Map<String,Integer> tmp = new HashMap<>();
                    List<Integer> tmpList = apDataInteger.get(result.BSSID);
                    tmpList.add(result.level);
                    apDataInteger.put(result.BSSID,tmpList);
                }
            }
        }

        //PARSE AP's LEVEL FORM INTEGER TO STRING TABLE
        for (String uniqeBSSID : uniqueApBSSID){
            List <Integer> tmp = apDataInteger.get(uniqeBSSID);
            String dataString = "[";

            for (Integer i=0; i<tmp.size(); i++){
                if (i != tmp.size() -1){
                    dataString += tmp.get(i).toString() + ",";
                }else{
                    dataString += tmp.get(i).toString();
                }
            }

            dataString += "]";
            Map<String,String> tmpMap = new HashMap<>();
            tmpMap.put(uniqeBSSID,dataString);
            apDataString.put(uniqeBSSID,tmpMap);
        }

        Map<String,String> map = new HashMap<>();
        for (List<ScanResult> dataList : apInfoList) {
            for (ScanResult result: dataList){
                map.put(CONSTANT_MAGNETIC_JSON.get("MAC_AP"),result.BSSID);
                map.put(CONSTANT_MAGNETIC_JSON.get("SSID"),result.SSID);
                map.put(CONSTANT_MAGNETIC_JSON.get("PLACE"),place_name);
                map.put(CONSTANT_MAGNETIC_JSON.get("POSITIONS"),changePositonsToString());
                map.put(CONSTANT_MAGNETIC_JSON.get("TIMESTAMP"),timeStamp());
                map.put(CONSTANT_MAGNETIC_JSON.get("RSSI_DATA"),apDataString.get(result.BSSID).get(result.BSSID));
                map.put(CONSTANT_MAGNETIC_JSON.get("RSSI_AVG_TIME"),timeToString(RSSI_CHOICE));
                map.put(CONSTANT_MAGNETIC_JSON.get("IP_PHONE"),phone_ip.toString());
                map.put(CONSTANT_MAGNETIC_JSON.get("MAC_PHONE"),phone_mac);

                list.add(map);
                map.clear();
            }

        }
        printStep("PARSE MAGNETOMETER END");
    }

  private void preapreStringEntity() {

        printStep("CREATE STRING ENTITY");
        try {
            for (JSONObject item : jsonMagnetic) {
                Log.i("GAIN DATA: ", "CREATE MAGNETIC STRING ENTITY");
                String tmp = item.toString();
                entityRssi.add(new StringEntity(tmp));
            }
            for (JSONObject item : jsonRssi) {
                Log.i("GAIN DATA: ", "CREATE RSSI STRING ENTITY");
                String tmp = item.toString();
                entityRssi.add(new StringEntity(tmp));
            }
        } catch (UnsupportedEncodingException e) {
            e.printStackTrace();
        }
        Log.i("GAIN DATA: ", "String entity gotowe");
    }


    private void startMagnetometer() {

        printStep("START MAGNETOMETER");
        mSensorManager.registerListener((SensorEventListener) this, mSensor, SensorManager.SENSOR_DELAY_FASTEST, SensorManager.SENSOR_STATUS_ACCURACY_HIGH);

    }


    private void stopMagnetometer() {
        if (magneticCounter == DATA_SIZE) {
            mSensorManager.unregisterListener(this);
            mSensor=null;
            Integer size = magneticList.size();
            Log.i("GAIN DATA - INFO", size.toString());
            //rawDataMagnetic.add(magneticList);
            //magneticList.clear();
            //prepareJson(0);
        }
    }

    @Override
    public void onSensorChanged(SensorEvent event) {
        if (event.sensor.getType() == Sensor.TYPE_MAGNETIC_FIELD) {
            Log.i("GAIN DATA: ", "IN MAGNETIC SENSOR");
            getMagnetic(event);

        }
    }

    private void  getMagnetic(SensorEvent event){
        startTime();
        List<Float> tmp = new ArrayList<Float>();
        tmp.add(event.values[0]);
        tmp.add(event.values[1]);
        tmp.add(event.values[2]);
        Log.i("GAIN DATA - Magnetyzm x : ", tmp.get(0).toString());
        Log.i("GAIN DATA - Magnetyzm y : ", tmp.get(1).toString());
        Log.i("GAIN DATA - Magnetyzm z : ", tmp.get(2).toString());
        magneticList.add(tmp.get(0));
        magneticList.add(tmp.get(1));
        magneticList.add(tmp.get(2));
        magneticCounter++;
        stopTime(MAGNETIC_CHOICE);
        stopMagnetometer();
    }

    @Override
    public void onAccuracyChanged (Sensor sensor,int accuracy){

    }

    private void gainRssi() {
        printStep();

        while (true) {
            startTime();
            wifiManager.startScan();
            Log.i("GAIN DATA - INFO",wifiManager.getScanResults().get(0).getClass().toString());
            apInfoList.add(wifiManager.getScanResults());
            //wifiSeen.get(0).
            apInfoCounter++;
            stopTime(RSSI_CHOICE);
            if (apInfoCounter == DATA_SIZE) {
                break;
            }

            Log.i("GAIN DATA - INFO", "Parsowanie danych");
            //prepareJson( 1);
        }
    }

    private void gainPhoneInfo(){
        WifiInfo wInfo = wifiManager.getConnectionInfo();
        phone_mac = wInfo.getMacAddress();
        phone_ip = wInfo.getIpAddress();

    }


    public void printStep(){
        String msg = "GAIN DATA - KROK " + printCounter.toString();
        Log.i("GAIN DATA - KROK nr ", printCounter.toString());
        Toast.makeText(context, msg, Toast.LENGTH_LONG).show();
        printCounter ++;
    }

    public void printStep(String string){
        String msg = "GAIN DATA - KROK " + printCounter.toString() + "--" + string;
        Log.i("GAIN DATA - KROK nr ", printCounter.toString() + "--" + string);
        Toast.makeText(context, msg, Toast.LENGTH_LONG).show();
        printCounter ++;
    }


    private void startTime() {
        this.startTime = System.nanoTime();

    }

    private void stopTime(Integer choice ) {
        Long difference = System.nanoTime() - startTime;
        this.timeList.get(choice).add(difference);
        this.startTime = Long.valueOf(0);

    }

    private void measureAvgTime(Integer choice ){

        Long sum = Long.valueOf(0);
        Float avg = Float.valueOf(0);
        Float length = new Float(timeList.get(choice).size());

        for (Long time : timeList.get(choice)) {
            sum += time;

        }

        avg = sum/length;

        Map tmp = new HashMap();
        tmp.put(choice, avg);
        avgTimeList.add(tmp);
    }

    private void measureTimes(){
        measureAvgTime(MAGNETIC_CHOICE);
        measureAvgTime(RSSI_CHOICE);
    }

    private class HttpAsyncTask extends AsyncTask<String, Void, String> {
        @Override
        protected String doInBackground(String... urls) {
            sendData();

            return  "";
        }

    }

    public String sendData(){

        try {

            HttpParams httpParameters = new BasicHttpParams();
            int timeoutConnection = 4000;
            Log.i("GAIN ACTIVITY: ", "11111111111");
            HttpConnectionParams.setConnectionTimeout(httpParameters, timeoutConnection);
            int timeoutSocket = 6000;
            Log.i("GAIN ACTIVITY: ", "2222222222222222");
            HttpConnectionParams.setSoTimeout(httpParameters, timeoutSocket);
            Log.i("GAIN ACTIVITY: ", "3333333333333333333");
            HttpClient httpclient = new DefaultHttpClient();
            URI absolute = new URI("http://192.168.1.40:8080");
            Log.i("GAIN ACTIVITY: ", "44444444444444444444444");


            HttpPost httpPost = new HttpPost(absolute);
            Log.i("MAIN ACTIVITY: ", "66666666666666666666");
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


        }catch(Exception e){
            e.printStackTrace();
        }
        return "";
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

}
