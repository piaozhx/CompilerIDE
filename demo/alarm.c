int h;
int m;
int s;
int c;
int time;
int alarm_h;
int alarm_m;
int alarm_s;
int alarm_mode;
int select_loc;

void delay()
{
    c = 40000;
    while(c){c=c-1;}
}

void get_real_time()
{
    time = h*10000 + m*100 + s;
}

void get_alarm_time()
{
    time = alarm_h*10000 + alarm_m*100 + alarm_s;
}

void get_time()
{
    if(alarm_mode)
        {get_real_time();}
    else
    {get_alarm_time();}
}

void increase_time()
{
    if(s<59)
    {
        s = s+1;
    }
    else
    {
        s = 0;
        if(m<59)
        {
            m = m + 1;
        }
        else
        {
            m = 0;
            h = h + 1;
        }
    }
}

void increase_alarm_s()
{
    if(alarm_s<59)
    {
        alarm_s = alarm_s + 1;
    }
    else
    {
        alarm_s = 0;
    }
}

void increase_alarm_m()
{
    if(alarm_m<59)
    {
        alarm_m = alarm_m + 1;
    }
    else
    {
        alarm_m = 0;
    }
}

void increase_alarm_h()
{
    if(alarm_h<23)
    {
        alarm_h = alarm_h + 1;
    }
    else
    {
        alarm_h = 0;
    }
}

void decrease_alarm_s()
{
    if(alarm_s)
    {
        alarm_s = alarm_s - 1;
    }
    else
    {
        alarm_s = 59;
    }
}

void decrease_alarm_m()
{
    if(alarm_m)
    {
        alarm_m = alarm_m - 1;
    }
    else
    {
        alarm_m = 59;
    }
}

void decrease_alarm_h()
{
    if(alarm_h)
    {
        alarm_h = alarm_h - 1;
    }
    else
    {
        alarm_h = 23;
    }
}

int main()
{
    int led;
    led = 1000;
    alarm_mode = 0;
    select_loc = 0;

    while(1)
    {
        delay();
        increase_time();
        get_time();
        $led = time;
    }
}

void interrupt_0()
{
    alarm_mode = !alarm_mode;
}

void interrupt_1()
{
    if((select_loc<3) && (alarm_mode))
    {
        select_loc = select_loc +1;
    }
}

void interrupt_2()
{
    if((select_loc) && (alarm_mode))
    {
        select_loc = select_loc - 1;
    }
}


void interrupt_3()
{
    if(alarm_mode)
    {
        if(select_loc == 0)
        {
            increase_alarm_s();
        }
        else
        {
            if (select_loc == 1)
            {
                increase_alarm_m();
            }
            else
            {
                increase_alarm_h();
            }
        }
    }
}

void interrupt_4()
{
    if(alarm_mode)
    {
        if(select_loc == 0)
        {
            decrease_alarm_s();
        }
        else
        {
            if (select_loc == 1)
            {
                decrease_alarm_m();
            }
            else
            {
                decrease_alarm_h();
            }
        }
    }
}
