#include "QSKDefines.h"
#include "proto.h"
#include "extern.h"
#include "string.h"
#include "stdlib.h"

/***********************************************************************/
/*                                                                     */
/*  DATE        :Mon, Mar 23, 2009                                     */
/*																	   */
/*  DESCRIPTION :  This file contains all the interrupt routines for   */
/* 	  				the peripherals.  								   */
/*																	   */
/*  CPU GROUP   :62P                                                   */
/*                                                                     */
/*  Copyright (c) 2009 by BNS Solutions, Inc.						   */
/*  All rights reserved.											   */
/*                                                                     */
/***********************************************************************/

#pragma INTERRUPT A2DInterrupt
#pragma INTERRUPT UART0TransmitInterrupt
#pragma INTERRUPT UART0ReceiveInterrupt
#pragma INTERRUPT TimerA1Interrupt
#pragma INTERRUPT TimerA2Interrupt
#pragma INTERRUPT KeyBoardInterrupt
#pragma INTERRUPT DMA0Interrupt
#pragma INTERRUPT WakeUpInterrupt
#pragma INTERRUPT RTCInterrupt
#pragma INTERRUPT TimerB0Interrupt
#pragma INTERRUPT WatchDogInterrupt

char command[20];
char pivalue[20];
int pinum;
int i = 0;

void A2DInterrupt(void)
//-----------------------------------------------------------------------------------------------------
//  Purpose:	Unused in this program
//  
//
//  Rev:    1.0     Initial Release
//  
//  Notes:          None    
//-----------------------------------------------------------------------------------------------------
{
}

void UART0TransmitInterrupt(void)
//-----------------------------------------------------------------------------------------------------
//  Purpose:	Unused in this program
//  
//
//  Rev:    1.0     Initial Release
//  
//  Notes:          None    
//-----------------------------------------------------------------------------------------------------
{
}

void DMA0Interrupt(void)
//-----------------------------------------------------------------------------------------------------
//  Purpose:	Unused in this program
//  
//
//  Rev:    1.0     Initial Release
//  
//  Notes:          None    
//-----------------------------------------------------------------------------------------------------
{
}

void UART0ReceiveInterrupt(void)
//-----------------------------------------------------------------------------------------------------
//  Purpose:	Unused in this program
//  
//
//  Rev:    1.0     Initial Release
//  
//  Notes:          None    
//-----------------------------------------------------------------------------------------------------
{
	int j;
	char* token;
	char data;
	while(ri_u0c1 == 0);	 // make sure receive is complete
	
	data = (char) u0rb;
	
	// Get command
	if(data == '$')
	{
		command[i] = (char) u0rb;
		i++;
		
		// Build p-value
		for(i = 1; i < strlen(command); i++)
		{
			if(command[i] == '$')
			{
				pivalue[i - 1] = '\0';
				pinum = atoi(pivalue);
				
				// Parse packet for new alert temp
				if(command[0] == 'T')
				{
					alert_temp = pinum;
				}
				
				// Parse packet for new serial settings
				else if(command[0] == 'B')
				{
					// Get first token
					token = strtok(command, ",");
					
					// Get rest of tokens
					while(token != NULL)
					{	
						// Parse baud rate	
						if(token[0] == 'B')
						{
							pinum = atoi(token+1);
							
							u0brg = (unsigned char)(((f1_CLK_SPEED/16)/pinum)-1);
						}
								
						// Parse num bits								
						if(token[0] == 'N')
						{
							pinum = atoi(token+1);
							
							if(pinum == 7)
							{
								u0mr = u0mr | 0x04;
							}
							else if(pinum == 8)
							{
								u0mr = u0mr | 0x05;	
							}
							else
							{
								u0mr = u0mr | 0x06;
							}
						}
						// Parse parity
						else if(token[0] == 'P')
						{
							pinum = atoi(token+1);
							
							if(pinum == 0)
							{	
								u0mr ^= (-1^u0mr) &(1 << 6);
								u0mr ^= (-0^u0mr) &(1 << 5);
							}
							else if(pinum == 1)
							{
								u0mr ^= (-1^u0mr) &(1 << 6);
								u0mr ^= (-1^u0mr) &(1 << 5);
							}
							else
							{
								u0mr ^= (-0^u0mr) &(1 << 6);
								u0mr ^= (-0^u0mr) &(1 << 5);
							}
						}
						
						// Parse stop bits
						else if(token[0] == 'S')
						{
							pinum = atoi(token+1);
							
							if(pinum == 1)
							{
								u0mr ^= (-0^u0mr) &(1 << 4);
							}
							else if(pinum == 2)
							{
								u0mr ^= (-1^u0mr) &(1 << 4);
							}
						}

						// Retoken
						token = strtok(NULL, ",");
					}
				}
				
				for(j = 0; j < 20; j++)
				{
					command[j] = 0;
					pivalue[j] = 0;
				}
				
				i = 0;
				token = NULL;
				break;
			}
			else
			{
				pivalue[i - 1] = command[i];
			}
		}
	}
	else
	{
		command[i] = (char) u0rb;
		i++;
	}
}

void TimerA1Interrupt(void)
//-----------------------------------------------------------------------------------------------------
//  Purpose:	This handles the interrupt for Timer A1. It will start an A2D every time in.
//  
//
//  Rev:    1.0     Initial Release
//  
//  Notes:          None    
//-----------------------------------------------------------------------------------------------------
{
// Uncomment the lines "//$" below to read the two channels every other timer 
// interrupt instead of every interrupt
    
//$    static unsigned char adSwitch;
    
//$    if (adSwitch == 0) {    // read the a/d channel every other entry.
//$        adSwitch = 1;

    	adcon0 = 0x80;	// AN0, One-shot, software trigger, fAD/2
        adst = 1;				// Start A2D conversion	
    	while(adst == 1);		// wait for A/D conversion start bit to return to 0 read AD value 
    	ta1 = ad0 + 10;			// and preload Timer A1 to vary the LED switching rate 
    							// (the + 10 is to ensure the counter is not loaded with 0"
    	A2DValue = ad0;
        A2DValuePot = A2DValue;
//$    }
//$    else {
//$        adSwitch = 0;
    	adcon0 = 0x81;	// AN0, One-shot, software trigger, fAD/2
        adst = 1;				// Start A2D conversion	
    	while(adst == 1);		// wait for A/D conversion start bit to return to 0 

    	A2DValueTherm = ad1;
//$    }						
                            
	++disp_count;			// increment display control variable 
	if (disp_count > 4){	// if LED control variable exceeds valid number 
		disp_count = 1;		// return to initial state 
	}
	
    A2DProcessed = TRUE;	// only update the display when a new value is available
	
}

void TimerA2Interrupt(void)
//-----------------------------------------------------------------------------------------------------
//  Purpose:	Unused in this program
//  
//
//  Rev:    1.0     Initial Release
//  
//  Notes:          None    
//-----------------------------------------------------------------------------------------------------
{
}

void KeyBoardInterrupt(void)
//-----------------------------------------------------------------------------------------------------
//  Purpose:	Unused in this program
//  
//
//  Rev:    1.0     Initial Release
//  
//  Notes:          None    
//-----------------------------------------------------------------------------------------------------
{
}

void WakeUpInterrupt(void)
//-----------------------------------------------------------------------------------------------------
//  Purpose:	Unused in this program
//  
//
//  Rev:    1.0     Initial Release
//  
//  Notes:          None    
//-----------------------------------------------------------------------------------------------------
{
}

void RTCInterrupt(void)
//-----------------------------------------------------------------------------------------------------
//  Purpose:	Unused in this program
//  
//
//  Rev:    1.0     Initial Release
//  
//  Notes:          None    
//-----------------------------------------------------------------------------------------------------
{
}

void TimerB0Interrupt(void)
//-----------------------------------------------------------------------------------------------------
//  Purpose:	Unused in this program
//  
//
//  Rev:    1.0     Initial Release
//  
//  Notes:          None    
//-----------------------------------------------------------------------------------------------------
{
}

void WatchDogInterrupt(void)
//-----------------------------------------------------------------------------------------------------
//  Purpose:	Unused in this program
//  
//
//  Rev:    1.0     Initial Release
//  
//  Notes:          None    
//-----------------------------------------------------------------------------------------------------
{
}

