#include "QSKDefines.h"
#include "proto.h"
#include "extern.h"
#include "math.h"

/***********************************************************************/
/*                                                                     */
/*  DATE        :Mon, Mar 23, 2009                                     */
/*																	   */
/*  DESCRIPTION :      This is the main file for the project and       */
/* 	  					contains most of the project specific code     */
/*																	   */
/*  CPU GROUP   :62P                                                   */
/*                                                                     */
/*  Copyright (c) 2009 by BNS Solutions, Inc.						   */
/*  All rights reserved.											   */
/*                                                                     */
/***********************************************************************/
int disp_count;				// LED control variable
uint A2DValue;
uint A2DValuePot;
uint A2DValueTherm;
uint btn1 = 0; 
uint btn2 = 0; 
uint btn3 = 0;
uchar A2DProcessed;
int alert_temp = 85;

void main(void)
//-----------------------------------------------------------------------------------------------------
//  Purpose:	The MCU will come here after reset. 
//  
//
//  Rev:    1.0     Initial Release
//  
//  Notes:          None    
//-----------------------------------------------------------------------------------------------------
{
	unsigned int f1;
	unsigned int f2;
	unsigned int f3;
	int prev_alert_temp = 0;
	float prevT = 0.0;
	float B = 3960.0;
	float r0 = 10000.0;
	float t0 = 298.15;
	float t = 1.0;
	float r = 0.0;
	MCUInit();
	InitDisplay(" ");
	InitUART();
  	TimerInit();
	ADInit();	
	ENABLE_SWITCHES;
	
	/* LED initialization - macro defined in qsk_bsp.h */
 	ENABLE_LEDS;
	pd0_0 = 1;
	p0_0 = 1;

	while(1)
	{
		// Get resist
		r = 10000.0 * A2DValueTherm / (1024.0 - A2DValueTherm);
					
		// Get temperature in kelvin
		t = B * t0 / (t0 * log(r / r0) + B);
		
		// Convert to C
		t -= 273.15;
		
		// Convert to F
		t = (t * (9.0/5.0)) + 32.2;
			
		if(prevT != t && t > 0)
		{	
			// Turn on fan
			if(t > alert_temp)
			{
				p0_0 = 1;
			}
			else
			{
				p0_0 = 0;
			}
			
			// Print temp to serial + newline
			BNSPrintf(SERIAL,"TEMP:%0.2f\r\n", t);
			
			prevT = t;
		}
		
		// If button pressed
		if(S1 == 0 && f1 == 0)
		{
			f1 = 1;
			BNSPrintf(SERIAL, "ACTION:LBUT\r\n");
		}
		else if(S2 == 0 && f2 == 0)
		{
			f2 = 1;
			BNSPrintf(SERIAL, "ACTION:CBUT\r\n");				
		}
		else if(S3 == 0 && f3 == 0)
		{
			f3 = 1;
			BNSPrintf(SERIAL, "ACTION:RBUT\r\n");				
		}
		
		if(S1 == 1)
			f1 = 0;
		if(S2 == 1)
			f2 = 0;
		if(S3 == 1)
			f3 = 0;
			
		// Set alert temp if it changes and print it
		if(alert_temp != prev_alert_temp)
		{
			prev_alert_temp = alert_temp;
		}
	}
}			

void TimerInit(void)
//-----------------------------------------------------------------------------------------------------
//  Purpose:	This will set up the A0 timer for 1ms and the A1 as counter
//  
//
//  Rev:    1.0     Initial Release
//  
//  Notes:          None    
//-----------------------------------------------------------------------------------------------------
{
   /* Configure Timer A0 - 1ms (millisecond) counter */
   ta0mr = 0x80;	// Timer mode, f32, no pulse output
   ta0 = (unsigned int) (((f1_CLK_SPEED/32)*1e-3) - 1);	// (1ms x 12MHz/32)-1 = 374
 
   /* Configure Timer A1 - Timer A0 used as clock */
   ta1mr = 0x01;	// Event Counter mode, no pulse output
   ta1 = 0x3FF;		// initial value - max value of ADC (0x3FF)
   trgsr = 0x02;	// Timer A0 as event trigger

/* The recommended procedure for writing an Interrupt Priority Level is shown
   below (see M16C datasheets under 'Interrupts' for details). */

   DISABLE_IRQ		// disable irqs before setting irq registers - macro defined in skp_bsp.h
   ta1ic = 3;		// Set the timer A1's IPL (interrupt priority level) to 3
   ENABLE_IRQ		// enable interrupts macro defined in skp_bsp.h

   /* Start timers */
   ta1s = 1;		// Start Timer A1
   ta0s = 1;		// Start timer A0
}


void ADInit(void)
//-----------------------------------------------------------------------------------------------------
//  Purpose:	Set up the A2D for one shot mode.
//  
//
//  Rev:    1.0     Initial Release
//  
//  Notes:          None    
//-----------------------------------------------------------------------------------------------------
{
   /* Configure ADC - AN0 (Analog Adjust Pot) */
   adcon0 = 0x80;	// AN0, One-shot, software trigger, fAD/2
   adcon1 = 0x28;	// 10-bit mode, Vref connected.
   adcon2 = 0x01;	// Sample and hold enabled
}   


void LEDDisplay(void)
//-----------------------------------------------------------------------------------------------------
//  Purpose:	Make the LEDs scan back and forth.
//  
//
//  Rev:    1.0     Initial Release
//  
//  Notes:          None    
//-----------------------------------------------------------------------------------------------------
{

	switch (disp_count){
		
		case 1:							/* green on */
   				LED0 = LED_OFF;			
				LED1 = LED_OFF;
				LED2 = LED_ON;
				break;
		case 2:							/* yellow on */
		case 4:
   				LED0 = LED_OFF;			
				LED1 = LED_ON;
				LED2 = LED_OFF;
				break;
		case 3:							/* red on */
   				LED0 = LED_ON;			
				LED1 = LED_OFF;
				LED2 = LED_OFF;
				break;
		default:						/* all LED's off */
   				LED0 = LED_OFF;			
				LED1 = LED_OFF;
				LED2 = LED_OFF;
	}
}