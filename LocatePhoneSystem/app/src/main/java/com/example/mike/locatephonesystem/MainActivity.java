package com.example.mike.locatephonesystem;


import android.content.Intent;
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


public class MainActivity extends ActionBarActivity implements View.OnClickListener {

    private static Float x = Float.valueOf(0);
    private static Float y = Float.valueOf(0);
    private static String place_name = "DEFAULT";
    private static String mode = "FEED_MAP";
    private static Integer chooseCheckPoint = 0;
    private static Float step_x = Float.valueOf(1);
    private static Float step_y = Float.valueOf(1);
    private static Integer dataSize = 100;

    private static EditText editText;
    private static EditText editText2;
    private static EditText editText3;







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

        editText = (EditText) findViewById(R.id.editText);
        editText2 = (EditText) findViewById(R.id.editText2);
        editText3 = (EditText) findViewById(R.id.editText3);


        //imm.hideSoftInputFromWindow(editText.getWindowToken(), InputMethodManager.HIDE_NOT_ALWAYS);
        //imm.hideSoftInputFromWindow(editText2.getWindowToken(), InputMethodManager.HIDE_NOT_ALWAYS);
        //imm.hideSoftInputFromWindow(editText3.getWindowToken(), InputMethodManager.HIDE_NOT_ALWAYS);

    }

    public void onClick(View v) {
        switch (v.getId()) {
            case  R.id.button: {
                Intent intent = new Intent(this, GainData.class);
                intent.putExtra(GainData.X_INTENT,x);
                intent.putExtra(GainData.Y_INTENT,y);
                intent.putExtra(GainData.PLACE_NAME_INTENT,place_name);
                intent.putExtra(GainData.MODE_INTENT, mode);
                intent.putExtra(GainData.CHOOSE_CHECKPOINT_INTENT, chooseCheckPoint);
                intent.putExtra(GainData.STEPX_INTENT, step_x);
                intent.putExtra(GainData.STEPY_INTENT,step_y);
                intent.putExtra(GainData.DATA_SIZE_INTENT,dataSize);
                startService(intent);
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
                String  [] tmpList = tmp.split(",");
                Log.i("MAIN STEP X:", tmpList[0]);
                Log.i("MAIN STEP Y:", tmpList[1]);
                this.step_x= Float.valueOf(tmpList[0]);
                this.step_y = Float.valueOf(tmpList[1]);
                String msg = "STEP_X: " + step_x.toString() + " STEP_Y: " + step_y.toString() + " PLACE_NAME: " + place_name;
                Toast.makeText(this, msg, Toast.LENGTH_LONG).show();
                break;
            }
            case R.id.button6:{
                Integer tmp = Integer.valueOf(editText2.getText().toString());
                if (tmp >=  21)
                    tmp =20;
                this.chooseCheckPoint = tmp;
                String msg = "CHECKPOINT: " + GainData.CHECKPOINTS[chooseCheckPoint];
                Toast.makeText(this, chooseCheckPoint.toString(), Toast.LENGTH_LONG).show();
                break;
            }
            case R.id.button7:{
                this.dataSize += 300;
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
}
