package com.example.mike.locatephonesystem;

import android.annotation.TargetApi;
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
import android.os.Build;
import android.os.IBinder;
import android.text.format.Formatter;
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
import org.json.JSONArray;
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
    public static final String MODE_INTENT = "MODE";
    public static final String CHOOSE_CHECKPOINT_INTENT = "CHECKPOINT";
    public static final String STEPX_INTENT = "STEPX";
    public static final String STEPY_INTENT = "STEPY";
    public static final String DATA_SIZE_INTENT = "DATA SIZE";

    private static final Integer MAGNETIC_CHOICE = 0;
    private static final Integer RSSI_CHOICE = 1;
    private static final Map<String,String> CONSTANT_JSON = new HashMap();
    static{
        //static fileds in json files
        CONSTANT_JSON.put("PLACE","PLACE");
        CONSTANT_JSON.put("POSITIONS","POSITIONS");
        CONSTANT_JSON.put("TIMESTAMP","TIMESTAMP");
        CONSTANT_JSON.put("MAGNETIC_DATA","MAGNETIC_DATA");
        CONSTANT_JSON.put("MAGNETIC_AVG_TIME","MAGNETIC_AVG_TIME");
        CONSTANT_JSON.put("IP_PHONE","IP_PHONE");
        CONSTANT_JSON.put("MAC_PHONE","MAC_PHONE");

        CONSTANT_JSON.put("SSID","SSID");
        CONSTANT_JSON.put("MAC_AP","MAC_AP");
        CONSTANT_JSON.put("RSSI_DATA","RSSI_DATA");
        CONSTANT_JSON.put("RSSI_AVG_TIME","RSSI_AVG_TIME");
        CONSTANT_JSON.put("FEED_MAP","FEED_MAP");
        CONSTANT_JSON.put("LOCATE_PHONE","LOCATE_PHONE");
        CONSTANT_JSON.put("MODE","MODE");
        CONSTANT_JSON.put("CHECKPOINT","CHECKPOINT");
        CONSTANT_JSON.put("STEP","STEP");
        CONSTANT_JSON.put("DATA_SIZE","DATA_SIZE");
    };
    public static final  String [] CHECKPOINTS = new String [] {"A", "B", "C", "D", "E", "F", "G", "H", "I", "J", "K", "L", "M", "N", "O", "P", "R", "S", "T", "U","ERROR"};

    private List<JSONObject> jsonMagnetic = new ArrayList<>();
    private List<JSONObject> jsonRssi = new ArrayList<>();
    public static  List<StringEntity> entity = new ArrayList<>();
    private List<Float> magneticList = new ArrayList<>();
    private List<List<ScanResult>> apInfoList = new ArrayList();
    private List<List<Long>> timeList = new ArrayList<>();
    private List<Map<String, Long>> avgTimeList = new ArrayList();



    private String place_name="DEFAULT";
    private Float x = Float.valueOf(0);
    private Float y = Float.valueOf(0);
    private String phone_ip="";
    private String phone_mac="";
    private String mode = "FEED_MAP";
    private Integer chooseCheckPoint = 0;
    private static List<Float> step = new ArrayList<Float> ();
    static {
        step.add(Float.valueOf(1));
        step.add(Float.valueOf(1));
    };

    private Integer printCounter = 0;
    private Integer magneticCounter = 0;
    private Integer apInfoCounter = 0;
    private Long startTime = Long.valueOf(0);
    private static Integer DATA_SIZE = 100;


    private void preapreService(){
        this.context = this;
        Log.i("GAIN DATA: ", context.toString());
        this.wifiManager = (WifiManager) getSystemService(Context.WIFI_SERVICE);

        this.place_name = "DEFAULT";
        this.timeList.add(new ArrayList<Long>());
        this.timeList.add(new ArrayList<Long>());
        this.gainPhoneInfo();

        try{
            this.mSensorManager = (SensorManager) getSystemService(Context.SENSOR_SERVICE);
            if (mSensorManager == null)
                Log.i("GAIN DATA - ", "MANAGER IS NULL");
        }catch(Exception e){
            e.printStackTrace();
        }

        //List<Sensor> mmSensor = mSensorManager.getSensorList(Sensor.TYPE_MAGNETIC_FIELD);
        this.mSensor = mSensorManager.getDefaultSensor(Sensor.TYPE_MAGNETIC_FIELD);
        if (mSensor == null){
            Log.i("GAIN DATA - ", "sensor is null");
        }
    }
    @Override
    public void onCreate() {
        // The service is being created
        preapreService();
    }
    @Override
    public int onStartCommand(Intent intent, int flags, int startId) {
        // The service is starting, due to a call to startService()
        preapreService();
        x =intent.getFloatExtra(X_INTENT, 0);
        y =intent.getFloatExtra(Y_INTENT, 0);
        place_name = intent.getStringExtra(PLACE_NAME_INTENT);
        mode = intent.getStringExtra(MODE_INTENT);
        chooseCheckPoint = intent.getIntExtra(CHOOSE_CHECKPOINT_INTENT, 0);
        Float tmpX = intent.getFloatExtra(STEPX_INTENT,1);
        Float tmpY = intent.getFloatExtra(STEPY_INTENT,1);
        step.set(0,tmpX);
        step.set(0,tmpY);
        DATA_SIZE = intent.getIntExtra(DATA_SIZE_INTENT,100);
        //DATA_SIZE = 128;

        String msg = "x: "  + x.toString() + "y:" + y.toString() + " PLACE NAME: " + place_name ;
        printStep(msg);
        Log.i("STEP: ", step.toString());
        Log.i("MODE: ", mode);
        Log.i("CHECKPOINT", chooseCheckPoint.toString());
        Log.i("DATA SIZE", DATA_SIZE.toString());


        gainRssi();
        startMagnetometer();

        return 0;
    }

    private void afterMagnetometer(){
        measureTimes();
        prepareJson();
        preapreStringEntity();
        Log.i("GAIN DATA", "SENDING");
        //new HttpAsyncTask().execute("http://hmkcode.appspot.com/jsonservlet");
        //sendData();
        //resetTables();
        stopSelf();

    }

    private void afterMagnetometer_1(){
        measureTimes();
        prepareJson();
        preapreStringEntity();
    }



    @Override
    public IBinder onBind(Intent intent) {
        // A client is binding to the service with bindService()
        return null;
    }




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
        return this.entity;
    }

    public void resetTables(){
        try {
            this.jsonMagnetic.clear();
            this.jsonRssi.clear();
            this.entity.clear();
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

    private Map<String,JSONArray>  prepareData(){

        Map<String, JSONArray> resultMap = new HashMap<>();
            Map<String, List<Integer>> integerMap = new HashMap<>();
            List<String> uniqueApBSSID = new ArrayList<>();
            for (List<ScanResult> dataList : apInfoList) {
                for (ScanResult result : dataList) {
                    if (!uniqueApBSSID.contains(result.BSSID)) {
                        uniqueApBSSID.add(result.BSSID);
                        integerMap.put(result.BSSID, new ArrayList<Integer>());
                    }
                }

            }

            for (Integer i = 0; i < apInfoList.size(); i++) {
                for (ScanResult result : apInfoList.get(i)) {
                    if (uniqueApBSSID.contains(result.BSSID)) {
                        Map<String, Integer> tmp = new HashMap<>();
                        List<Integer> tmpList = integerMap.get(result.BSSID);
                        tmpList.add(result.level);
                        integerMap.put(result.BSSID, tmpList);
                    }
                }
            }

                for (String uniqueBSSID : uniqueApBSSID) {
                    List<Integer> tmp = integerMap.get(uniqueBSSID);
                    JSONArray tmpArray = new JSONArray();
                    for (Integer rssi : tmp) {
                        tmpArray.put(rssi);
                    }
                    resultMap.put(uniqueBSSID, tmpArray);
                }


            JSONArray jsonArrayM = new JSONArray();

            for (Float magnetic : magneticList){
                jsonArrayM.put(magnetic);
            }
            resultMap.put("MAGNETIC_DATA",jsonArrayM);


        return resultMap;
    }



    private void prepareJson() {
        Map<String, String> dataMagneticDict = new HashMap<>();
        List<Map<String, String>> dataRssiDict = new ArrayList<>();


        //preaprsing array amp for createing jsonobejct
        this.feedHashMap(dataMagneticDict, dataRssiDict);

        JSONObject jsonMagneticObject = new JSONObject();


        JSONArray jsonArray = new JSONArray();
        jsonArray.put(x);
        jsonArray.put(y);

        Map<String, JSONArray> dataJson = prepareData();

        JSONArray stepArray = new JSONArray();
        stepArray.put(step.get(0));
        stepArray.put(step.get(1));

        //prepare json MAGNETIC - FEED MAP

        Log.i("GAIN DATA MODE", mode);
        Boolean tt = mode.matches("FEED_MAP");
        Log.i("GAIN DATA MODE CHECK", tt.toString());
        if (mode.matches("FEED_MAP") ){
            try {
                Log.i("CONSTANT_MAGNETIC_JSON", CONSTANT_JSON.get("PLACE"));
                //Log.i("dataMagneticDict", dataMagneticDict.get("PLACE"));
                jsonMagneticObject.accumulate(CONSTANT_JSON.get("DATA_SIZE"),DATA_SIZE);
                jsonMagneticObject.accumulate(CONSTANT_JSON.get("MODE"),mode);
                jsonMagneticObject.accumulate(CONSTANT_JSON.get("STEP"),stepArray);
                jsonMagneticObject.accumulate(CONSTANT_JSON.get("PLACE"),dataMagneticDict.get("PLACE"));
                jsonMagneticObject.accumulate(CONSTANT_JSON.get("POSITIONS"),jsonArray);
                jsonMagneticObject.accumulate(CONSTANT_JSON.get("TIMESTAMP"),dataMagneticDict.get("TIMESTAMP"));
                jsonMagneticObject.accumulate(CONSTANT_JSON.get("MAGNETIC_DATA"),dataJson.get("MAGNETIC_DATA"));
                jsonMagneticObject.accumulate(CONSTANT_JSON.get("MAGNETIC_AVG_TIME"),dataMagneticDict.get("MAGNETIC_AVG_TIME"));
                jsonMagneticObject.accumulate(CONSTANT_JSON.get("IP_PHONE"),dataMagneticDict.get("IP_PHONE"));
                jsonMagneticObject.accumulate(CONSTANT_JSON.get("MAC_PHONE"),dataMagneticDict.get("MAC_PHONE"));
                Log.i("MAGNETIC JSONOBJECT -", jsonMagneticObject.toString());
                jsonMagnetic.add(jsonMagneticObject);
            } catch (JSONException e) {
                e.printStackTrace();
            }

            //CREATE JSON FOR ALL AP
            try {
                for (Map<String,String> tmpMap : dataRssiDict ){
                    JSONObject tmpJsonObject = new JSONObject();
                    tmpJsonObject.accumulate(CONSTANT_JSON.get("DATA_SIZE"),DATA_SIZE);
                    tmpJsonObject.accumulate(CONSTANT_JSON.get("MODE"),mode);
                    tmpJsonObject.accumulate(CONSTANT_JSON.get("STEP"),stepArray);
                    tmpJsonObject.accumulate(CONSTANT_JSON.get("MAC_AP"),tmpMap.get("MAC_AP"));
                    tmpJsonObject.accumulate(CONSTANT_JSON.get("SSID"),tmpMap.get("SSID"));
                    tmpJsonObject.accumulate(CONSTANT_JSON.get("PLACE"),tmpMap.get("PLACE"));
                    tmpJsonObject.accumulate(CONSTANT_JSON.get("POSITIONS"),jsonArray);
                    tmpJsonObject.accumulate(CONSTANT_JSON.get("TIMESTAMP"),tmpMap.get("TIMESTAMP"));
                    tmpJsonObject.accumulate(CONSTANT_JSON.get("RSSI_DATA"),dataJson.get(tmpMap.get("MAC_AP")));
                    tmpJsonObject.accumulate(CONSTANT_JSON.get("RSSI_AVG_TIME"),tmpMap.get("RSSI_AVG_TIME"));
                    tmpJsonObject.accumulate(CONSTANT_JSON.get("IP_PHONE"), tmpMap.get("IP_PHONE"));
                    tmpJsonObject.accumulate(CONSTANT_JSON.get("MAC_PHONE"), tmpMap.get("MAC_PHONE"));

                    Log.i("RSSI JSONOBJECT", tmpJsonObject.toString());
                    jsonRssi.add(tmpJsonObject);
                }
            } catch (JSONException e) {
                e.printStackTrace();
            }
        } else if (mode.matches("LOCATE_PHONE")){
            try {
                Log.i("CONSTANT_MAGNETIC_JSON", CONSTANT_JSON.get("PLACE"));
                //Log.i("dataMagneticDict", dataMagneticDict.get("PLACE"));
                jsonMagneticObject.accumulate(CONSTANT_JSON.get("DATA_SIZE"),DATA_SIZE.toString());
                jsonMagneticObject.accumulate(CONSTANT_JSON.get("MODE"),mode);
                jsonMagneticObject.accumulate(CONSTANT_JSON.get("STEP"),step);
                jsonMagneticObject.accumulate(CONSTANT_JSON.get("PLACE"),dataMagneticDict.get("PLACE"));
                jsonMagneticObject.accumulate(CONSTANT_JSON.get("TIMESTAMP"),dataMagneticDict.get("TIMESTAMP"));
                jsonMagneticObject.accumulate(CONSTANT_JSON.get("MAGNETIC_DATA"),dataMagneticDict.get("MAGNETIC_DATA"));
                jsonMagneticObject.accumulate(CONSTANT_JSON.get("MAGNETIC_AVG_TIME"),dataMagneticDict.get("MAGNETIC_AVG_TIME"));
                jsonMagneticObject.accumulate(CONSTANT_JSON.get("IP_PHONE"),dataMagneticDict.get("IP_PHONE"));
                jsonMagneticObject.accumulate(CONSTANT_JSON.get("MAC_PHONE"),dataMagneticDict.get("MAC_PHONE"));
                Log.i("MAGNETIC JSONOBJECT -", jsonMagneticObject.toString());
                jsonMagnetic.add(jsonMagneticObject);
            } catch (JSONException e) {
                e.printStackTrace();
            }

            //CREATE JSON FOR ALL AP
            try {
                for (Map<String,String> tmpMap : dataRssiDict ){
                    JSONObject tmpJsonObject = new JSONObject();
                    tmpJsonObject.accumulate(CONSTANT_JSON.get("DATA_SIZE"),DATA_SIZE.toString());
                    tmpJsonObject.accumulate(CONSTANT_JSON.get("MODE"),mode);
                    tmpJsonObject.accumulate(CONSTANT_JSON.get("CHECKPOINT"),String.valueOf(CHECKPOINTS[chooseCheckPoint]));
                    tmpJsonObject.accumulate(CONSTANT_JSON.get("MAC_AP"),tmpMap.get("MAC_AP"));
                    tmpJsonObject.accumulate(CONSTANT_JSON.get("SSID"),tmpMap.get("SSID"));
                    tmpJsonObject.accumulate(CONSTANT_JSON.get("PLACE"),tmpMap.get("PLACE"));
                    tmpJsonObject.accumulate(CONSTANT_JSON.get("TIMESTAMP"),tmpMap.get("TIMESTAMP"));
                    tmpJsonObject.accumulate(CONSTANT_JSON.get("RSSI_DATA"),tmpMap.get("RSSI_DATA"));
                    tmpJsonObject.accumulate(CONSTANT_JSON.get("RSSI_AVG_TIME"),tmpMap.get("RSSI_AVG_TIME"));
                    tmpJsonObject.accumulate(CONSTANT_JSON.get("IP_PHONE"), tmpMap.get("IP_PHONE"));
                    tmpJsonObject.accumulate(CONSTANT_JSON.get("MAC_PHONE"), tmpMap.get("MAC_PHONE"));

                    Log.i("RSSI JSONOBJECT", tmpJsonObject.toString());
                    jsonRssi.add(tmpJsonObject);
                }
            } catch (JSONException e) {
                e.printStackTrace();
            }
        }



    }



    //function feed Hash Map with data from measurement
    private void feedHashMap(Map<String,String> mapMagnetic, List<Map<String,String>> mapRssi){

        //MAGNETIC MAP
        //Log.i("GAIN DATA - positions - ", changePositonsToString());
        //Log.i("GAIN DATA - magnetic list -", magneticDataToString());
        mapMagnetic.put(CONSTANT_JSON.get("PLACE"),place_name);
        mapMagnetic.put(CONSTANT_JSON.get("POSITIONS"),changePositonsToString());
        mapMagnetic.put(CONSTANT_JSON.get("TIMESTAMP"),timeStamp());
        mapMagnetic.put(CONSTANT_JSON.get("MAGNETIC_DATA"),magneticDataToString());
        mapMagnetic.put(CONSTANT_JSON.get("MAGNETIC_AVG_TIME"), timeToString(MAGNETIC_CHOICE));
        mapMagnetic.put(CONSTANT_JSON.get("IP_PHONE"), phone_ip.toString());
        mapMagnetic.put(CONSTANT_JSON.get("MAC_PHONE"), phone_mac);

        //RSSI MAP
        prepareRssiMaps(mapRssi);

        //Log.i("GAIN DATA - magneticarray", mapMagnetic.get("POSITIONS"));
        Log.i("mapMagnetic", mapMagnetic.toString());
        Log.i("mapRssi", mapRssi.toString());
        Integer tmmmp = mapMagnetic.size();
        Log.i("GAIN DATA - MAGNETIC - SIZE - ", tmmmp.toString());
        Log.i("GAIN DATA - MAGNETIC - ", mapMagnetic.get("MAGNETIC_DATA"));
    }

    private String changePositonsToString(){


        String tmp = "[ "+ x.toString() + " , " + y.toString() +" ]";
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
        //Log.i("GAIN DATA:", tmp);
        tmp += "]";

        return tmp;
    }

    private String timeToString(Integer choice){
        String tmp = String.valueOf(avgTimeList.get(choice).get(choice));
        Log.i("GAIN DATA AVG: ", tmp);

        return tmp;
    }

    private void prepareRssiMaps(List<Map<String,String>> list){

        //printStep("CREATE JSON FOR ALL AP + MAGNETIC JSON");
        //TAKE UNIQUE BSSID
        Map<String,List<Integer>> apDataInteger = new HashMap<>();
        Map<String, Map<String,String>> apDataString = new HashMap<>();
        List<String> uniqueApBSSID = new ArrayList<>();
        Map<String,Map<String,String>> uniqueSSID = new HashMap<>();

        for (List<ScanResult> dataList : apInfoList) {
            for (ScanResult result : dataList) {
               if(!uniqueApBSSID.contains(result.BSSID) ){
                   uniqueApBSSID.add(result.BSSID);
                   Map<String,String> tmpMap = new HashMap();
                   tmpMap.put(result.BSSID,result.SSID);
                   uniqueSSID.put(result.BSSID, tmpMap);
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
            Log.i("GAIN DATA RSSI LIST - ",dataString);
            tmpMap.put(uniqeBSSID, dataString);
            apDataString.put(uniqeBSSID,tmpMap);
            Log.i("DATA BEFORE MAP - ", String.valueOf(apDataString.get(uniqeBSSID)));
        }


       /* Map<String,String> map = new HashMap<>();
        for (List<ScanResult> dataList : apInfoList) {
            for (ScanResult result: dataList){
                map.put(CONSTANT_JSON.get("MAC_AP"),result.BSSID);
                map.put(CONSTANT_JSON.get("SSID"),result.SSID);
                map.put(CONSTANT_JSON.get("PLACE"),place_name);
                map.put(CONSTANT_JSON.get("POSITIONS"),changePositonsToString());
                map.put(CONSTANT_JSON.get("TIMESTAMP"),timeStamp());
                map.put(CONSTANT_JSON.get("RSSI_DATA"),apDataString.get(result.BSSID).get(result.BSSID));
                map.put(CONSTANT_JSON.get("RSSI_AVG_TIME"),timeToString(RSSI_CHOICE));
                map.put(CONSTANT_JSON.get("IP_PHONE"),phone_ip.toString());
                map.put(CONSTANT_JSON.get("MAC_PHONE"),phone_mac);

                list.add(map);
                map.clear();
            }

        }*/


        for(String uniqeBSSID : uniqueApBSSID){

            Map<String,String> map = new HashMap<>();
            map.put(CONSTANT_JSON.get("MAC_AP"),uniqeBSSID);
            map.put(CONSTANT_JSON.get("SSID"),uniqueSSID.get(uniqeBSSID).get(uniqeBSSID));
            map.put(CONSTANT_JSON.get("PLACE"),place_name);
            map.put(CONSTANT_JSON.get("POSITIONS"),changePositonsToString());
            map.put(CONSTANT_JSON.get("TIMESTAMP"),timeStamp());
            map.put(CONSTANT_JSON.get("RSSI_DATA"),apDataString.get(uniqeBSSID).get(uniqeBSSID));
            map.put(CONSTANT_JSON.get("RSSI_AVG_TIME"),timeToString(RSSI_CHOICE));
            map.put(CONSTANT_JSON.get("IP_PHONE"),phone_ip.toString());
            map.put(CONSTANT_JSON.get("MAC_PHONE"), phone_mac);

            Log.i("DATA AP EACH - ", map.get("RSSI_DATA"));
            list.add(map);
            //map.clear();
        }

        Integer tmmmp = list.size();
        Log.i("MAPRSSI - ", tmmmp.toString());
        Log.i("DATA RSSSI", list.get(0).get("RSSI_DATA"));
        //Log.i("DATA 0", list.get(0).get("RSSI DATA"));
        printStep("PARSE MAGNETOMETER END");
    }

  private void preapreStringEntity() {

        printStep("CREATE STRING ENTITY");
        try {
            for (JSONObject item : jsonMagnetic) {
                Log.i("GAIN DATA: ", "CREATE MAGNETIC STRING ENTITY");
                String tmp = item.toString();
                entity.add(new StringEntity(tmp));
            }
            for (JSONObject item : jsonRssi) {
                Log.i("GAIN DATA: ", "CREATE RSSI STRING ENTITY");
                String tmp = item.toString();
                entity.add(new StringEntity(tmp));
            }
        } catch (UnsupportedEncodingException e) {
            e.printStackTrace();
        }
        Log.i("GAIN DATA: ", "String entity gotowe");
    }


    private void startMagnetometer() {

        printStep("START MAGNETOMETER");
        try{
            mSensorManager.registerListener(this, mSensor, SensorManager.SENSOR_DELAY_FASTEST, SensorManager.SENSOR_STATUS_ACCURACY_HIGH);
        }catch(Exception e){
            e.printStackTrace();
        }

    }


    private void stopMagnetometer() {

        Log.i("IS TRUE: ", magneticCounter.toString());
        if (magneticCounter.equals(DATA_SIZE) ) {
            mSensorManager.unregisterListener(this);
            mSensorManager = null;
            mSensor=null;
            Integer size = magneticList.size();
            Log.i("GAIN DATA - INFO", size.toString());
            //rawDataMagnetic.add(magneticList);
            //magneticList.clear();
            //prepareJson(0);
            afterMagnetometer_1();
        }
    }

    @TargetApi(Build.VERSION_CODES.KITKAT_WATCH)
    @Override
    public void onSensorChanged(SensorEvent event) {
        Log.i("ON SENSOR CHANGED - ", "MAGNETIC IN");
        if (mSensor != null) {
            Log.i("GAIN DATA: ", "IN MAGNETIC SENSOR");
            startTime();
            getMagnetic(event);

        }
    }

    private void  getMagnetic(SensorEvent event){
        stopTime(MAGNETIC_CHOICE);
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
        stopMagnetometer();
    }

    @Override
    public void onAccuracyChanged (Sensor sensor,int accuracy){

    }

    private void gainRssi() {
        printStep();

        for(Integer i=0; i<DATA_SIZE;i++) {
            startTime();
            wifiManager.startScan();

            Log.i("GAIN DATA - INFO", wifiManager.getScanResults().get(0).getClass().toString());
            apInfoList.add(wifiManager.getScanResults());
            //wifiSeen.get(0).
            apInfoCounter++;
            Log.i("DATA SIZE", DATA_SIZE.toString());
            Log.i("DATA counter", i.toString());
            stopTime(RSSI_CHOICE);
            /*if (apInfoCounter == DATA_SIZE) {
                Log.i("DATA SIZE", "DATAAAAAAAA");
                break;
            }*/

            Log.i("GAIN DATA - INFO", "Parsowanie danych");
            //prepareJson( 1);
        }
    }

    private void gainPhoneInfo(){
        WifiInfo wInfo = wifiManager.getConnectionInfo();
        phone_mac = wInfo.getMacAddress();
        Integer tmp = wInfo.getIpAddress();
        phone_ip = Formatter.formatIpAddress(tmp);

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
        Toast.makeText(this, msg, Toast.LENGTH_LONG).show();
        printCounter ++;
    }


    private void startTime() {
        this.startTime =  System.nanoTime();

    }

    private void stopTime(Integer choice ) {
        Long difference = System.nanoTime() - startTime;
        this.timeList.get(choice).add(difference);
        this.startTime = Long.valueOf(0);

    }

    private void measureAvgTime(Integer choice ){

        Long sum = Long.valueOf(0);
        Long avg = Long.valueOf(0);
        Long length = new Long(timeList.get(choice).size());

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







}
