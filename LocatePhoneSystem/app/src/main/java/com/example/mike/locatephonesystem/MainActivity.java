package com.example.mike.locatephonesystem;


import android.app.Activity;
import android.content.Context;
import android.content.Intent;
import android.net.ConnectivityManager;
import android.net.NetworkInfo;
import android.os.AsyncTask;
import android.os.Bundle;
import android.support.v7.app.ActionBarActivity;
import android.util.Log;
import android.view.Menu;
import android.view.MenuItem;
import android.view.View;
import android.view.inputmethod.InputMethodManager;
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

import java.net.URI;
import java.util.Random;
import java.util.concurrent.ExecutionException;



public class MainActivity extends ActionBarActivity implements View.OnClickListener {

    public Random random = new Random();
    private static final int RANDOM_STR_LENGTH = 12;
    private static final String _CHAR = "ABCDEFGHIJKLMNOPQRSTUVWXYZ1234567890";

    private static Float x = Float.valueOf("0");
    private static Float y = Float.valueOf("0");
    private static String place_name = "DEFAULT";
    private static String mode = "FEED_MAP";
    private static String chooseCheckPoint = String.valueOf('a');
    private static Float step_x = Float.valueOf(1);
    private static Float step_y = Float.valueOf(1);
    private static Integer dataSize = 100;
    private static String hash = "DEFAULT";

    public Integer counterMsg = 0;

    private static EditText editText;
    private static EditText editText2;
    private static EditText editText3;

    private static TextView textView;

    private Intent intent;





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
        Button button5 = (Button) findViewById(R.id.button5);
        button5.setOnClickListener(this);
        Button button6 = (Button) findViewById(R.id.button6);
        button6.setOnClickListener(this);
        Button button7 = (Button) findViewById(R.id.button7);
        button7.setOnClickListener(this);
        Button button8 = (Button) findViewById(R.id.button8);
        button8.setOnClickListener(this);
        Button button9 = (Button) findViewById(R.id.button9);
        button9.setOnClickListener(this);
        Button button10 = (Button) findViewById(R.id.button10);
        button10.setOnClickListener(this);
        Button button11 = (Button) findViewById(R.id.button11);
        button11.setOnClickListener(this);
        Button button12 = (Button) findViewById(R.id.button12);
        button12.setOnClickListener(this);

        editText = (EditText) findViewById(R.id.editText);
        editText2 = (EditText) findViewById(R.id.editText2);
        editText3 = (EditText) findViewById(R.id.editText3);

        textView = (TextView) findViewById(R.id.textView);



        //imm.hideSoftInputFromWindow(editText.getWindowToken(), InputMethodManager.HIDE_NOT_ALWAYS);
        //imm.hideSoftInputFromWindow(editText2.getWindowToken(), InputMethodManager.HIDE_NOT_ALWAYS);
        //imm.hideSoftInputFromWindow(editText3.getWindowToken(), InputMethodManager.HIDE_NOT_ALWAYS);

    }

    public void onClick(View v) {
        switch (v.getId()) {
            case  R.id.button: {
                try {
                    counterMsg =0;
                    intent.putExtra(GainData.X_INTENT, x);
                    intent.putExtra(GainData.Y_INTENT, y);
                    intent.putExtra(GainData.PLACE_NAME_INTENT, place_name);
                    intent.putExtra(GainData.MODE_INTENT, mode);
                    intent.putExtra(GainData.CHOOSE_CHECKPOINT_INTENT, chooseCheckPoint);
                    intent.putExtra(GainData.STEPX_INTENT, step_x);
                    intent.putExtra(GainData.STEPY_INTENT, step_y);
                    intent.putExtra(GainData.DATA_SIZE_INTENT, dataSize);
                    intent.putExtra(GainData.HASH_INTENT, hash);
                    startService(intent);
                }catch (Exception ex){
                    ex.printStackTrace();
                }
                break;

            }

            case R.id.button2:{
                if (this.mode == "FEED_MAP"){
                    this.mode = "LOCATE_PHONE";
                    Toast.makeText(this, mode, Toast.LENGTH_LONG).show();
                }else if (this.mode == "LOCATE_PHONE"){
                    this.mode = "FEED_MAP";
                    String msg = "MODE: " + mode;
                    Toast.makeText(this, msg, Toast.LENGTH_LONG).show();
                }
                break;
            }

            case R.id.button3:{
                x +=step_x;
                String msg = "X: " + x.toString();
                Toast.makeText(this, msg, Toast.LENGTH_LONG).show();
                break;
            }
            case R.id.button4:{
                y +=step_y;
                String msg = "Y: " + y.toString();
                Toast.makeText(this, msg, Toast.LENGTH_LONG).show();
                break;
            }
            case R.id.button5:{
                this.place_name=editText.getText().toString();
                String tmp = editText3.getText().toString();
                String[] tmpList = tmp.split(",");
                if( tmp.equals("")){
                    Log.i("MAIN STEP X:", String.valueOf(1));
                    Log.i("MAIN STEP Y:", String.valueOf(1));
                    this.step_x= Float.valueOf(1);
                    this.step_y = Float.valueOf(1);
                }else {
                    Log.i("MAIN STEP X:", tmpList[0]);
                    Log.i("MAIN STEP Y:", tmpList[1]);
                    this.step_x = Float.valueOf(tmpList[0]);
                    this.step_y = Float.valueOf(tmpList[1]);
                }
                String msg = "STEP_X: " + step_x.toString() + " STEP_Y: " + step_y.toString() + " PLACE_NAME: " + place_name;
                Toast.makeText(this, msg, Toast.LENGTH_LONG).show();
                break;
            }
            case R.id.button6:{
                String tmp = editText2.getText().toString();
                //if (tmp >=  21)
                 //   tmp =20;
                this.chooseCheckPoint = tmp;
                String msg = "CHECKPOINT: " + chooseCheckPoint;
                Toast.makeText(this, chooseCheckPoint, Toast.LENGTH_LONG).show();
                break;
            }
            case R.id.button7:{
                this.dataSize += 100;
                String msg = "data size: " + dataSize.toString();
                Toast.makeText(this, msg, Toast.LENGTH_LONG).show();
                break;
            }
            case R.id.button8:{
                this.x = Float.valueOf(0);
                this.y = Float.valueOf(0);
                String msg = "x: " + x.toString() + " y: " + y.toString();
                Toast.makeText(this, msg, Toast.LENGTH_LONG).show();
                break;
            }
            case R.id.button9:{
                this.dataSize = 100;
                String msg = "data size: " + dataSize.toString();
                Toast.makeText(this, msg, Toast.LENGTH_LONG).show();
                break;
            }
            case R.id.button10:{
                String msg = "/" + String.valueOf(GainData.entity.size());
                for (Integer i =0; i<GainData.entity.size();i++){
                    HttpAsyncTask task = new HttpAsyncTask(i);
                    task.execute("http://hmkcode.appspot.com/jsonservlet");
                    try {
                        Integer tmpCounter = Integer.valueOf(task.get());
                        counterMsg += tmpCounter;

                    } catch (InterruptedException e) {
                        e.printStackTrace();
                    } catch (ExecutionException e) {
                        e.printStackTrace();
                    }
                    String tmp = counterMsg.toString() + msg;
                    textView.setText(tmp);
                    //Toast.makeText(this, tmp, Toast.LENGTH_LONG).show();
                }

                Toast.makeText(this, "SEND DATA", Toast.LENGTH_LONG).show();
                break;
            }
            case R.id.button11:{
                if (intent != null){
                    stopService(intent);
                    intent = null;
                }
                intent = new Intent(this, GainData.class);
                Toast.makeText(this, "NEW INTENT", Toast.LENGTH_LONG).show();
                counterMsg =0;
                textView.setText("B");
                break;
            }

            case R.id.button12:{
                 hash = getRandomString();
                Toast.makeText(this,"HASH: " + hash, Toast.LENGTH_LONG).show();
                break;
            }
        }
    }


        @Override
    public boolean onCreateOptionsMenu(Menu menu) {
        // Inflate the menu; this adds items to the action bar if it is present.
        getMenuInflater().inflate(R.menu.menu_main, menu);
        return true;
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
    }

    @Override
    protected void onPause() {
        super.onPause();
    }



    private class HttpAsyncTask extends AsyncTask<String, Void, String> {

        private Context context=null;
        private Integer index = 0;

        public HttpAsyncTask( Integer ind){
            index = ind;
        }
        @Override
        protected String doInBackground(String... urls) {

            StringEntity en = GainData.entity.get(index);
            //for (StringEntity en : GainData.entity){
                Log.i("GAIN DATA: ", "ASYNCTASK");
                sendData(en);
                Log.i("ASYNCTASK", "AFTER");


            //}
            Integer ret = 1;
            return  ret.toString();
        }


    }

    public String sendData(StringEntity en){

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
            //URI absolute = new URI("http://156.17.42.126:2080");
            URI absolute = new URI("http://192.168.1.19:8080");
            Log.i("GAIN ACTIVITY: ", "44444444444444444444444");


            HttpPost httpPost = new HttpPost(absolute);
            Log.i("MAIN ACTIVITY: ", "66666666666666666666");
            /*for (StringEntity en : entity){
                httpPost.setEntity(en);
            }*/
            httpPost.setEntity(en);

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
                    Log.i("MAIN ACTIVITY: ", "rrrrrrrrrrrrrrrrrrrr  ");
                }catch(Exception ex){
                    ex.printStackTrace();
                }

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

    private int getRandomNumber() {
        int randomInt = 0;
        randomInt = random.nextInt(_CHAR.length());
        if (randomInt - 1 == -1) {
            return randomInt;
        } else {
            return randomInt - 1;
        }
    }
    public String getRandomString(){

        StringBuffer randStr = new StringBuffer();

        for (int i = 0; i < RANDOM_STR_LENGTH; i++) {

            int number = getRandomNumber();
            char ch = _CHAR.charAt(number);
            randStr.append(ch);
        }
        return randStr.toString();
    }
}
