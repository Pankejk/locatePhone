package com.example.mike.locatephonesystem;


import android.content.Intent;
import android.os.Bundle;
import android.support.v7.app.ActionBarActivity;
import android.view.Menu;
import android.view.MenuItem;
import android.view.View;
import android.widget.Button;
import android.widget.EditText;
import android.widget.TextView;



public class MainActivity extends ActionBarActivity implements View.OnClickListener {

    private static Float x = Float.valueOf(0);
    private static Float y = Float.valueOf(0);
    private static String place_name = "DEFAULT";

    private static TextView textView;
    private static EditText editText;




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
    }

    public void onClick(View v) {
        switch (v.getId()) {
            case  R.id.button: {
                Intent intent = new Intent(this, GainData.class);
                intent.putExtra(GainData.X_INTENT,x);
                intent.putExtra(GainData.Y_INTENT,y);
                intent.putExtra(GainData.PLACE_NAME_INTENT,place_name);
                startService(intent);
                break;

            }

            case R.id.button2: {
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
