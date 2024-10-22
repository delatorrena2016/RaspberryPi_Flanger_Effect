#include <msp430.h> 

int Rx_Data; // set it to global variable to see it in debugger

int main(void)
{
	WDTCTL = WDTPW | WDTHOLD;	// stop watchdog timer
	
	// -- setup A0 SPI
	UCA0CTLW0 |= UCSWRST;  // put A0 into SW reset

	UCA0CTLW0 |= UCSSEL__SMCLK; // choose SMCLK
	UCA0BRW = 10; // set pre scale to 10 to get SCLK=1M/10=100KHz

	// -- set peripheral A0 into SPI mode

	UCA0CTLW0 |= UCSYNC; // put into synchronous mode (SPI)
	UCA0CTLW0 |= UCMST; // setting UCMST bit, or set to master

	// -- Configure Ports/Registers
	// set port 1 bit 0 (LED1) to output (O)
	P1DIR |= BIT0; //port 1 direction register set bit 0
	// LED1 = OFF initially
	P1OUT &= ~BIT0; // clear bit 0

	// same configuration for port 6 bit 6 (LED2) to output
	P6DIR |= BIT6;
	P6OUT &= ~BIT6;

	// -- setting switches, P4.1 (SW1) to input (I)

	P4DIR &= ~BIT1; // clear bit 1
	P4REN |= BIT1;  // turn on resistor
	P4OUT |= BIT1;  // makes resistor a Pull Up (PU)
	// We do an interrupt to trigger the off switch press
	P4IES |= BIT1; // port 4 Interrupt Edge Sensitivity, make sensitive to H-to-L

	// -- setting switches, P2.3 (SW2) to input (I)

	P2DIR &= ~BIT3;
	P2REN |= BIT3;
	P2OUT |= BIT3;
	P2IES |= BIT3;

	// set P4.1 (SW1) to input

	P1SEL1 &= ~BIT5; // P1SEL1,0 = 01 so to turn bit 5 to do s clock function
	P1SEL0 |= BIT5;

	P1SEL1 &= ~BIT7; // P1SEL1,0 = 01 so to turn bit 7 to do SIMO function
	P1SEL0 |= BIT7;

	P1SEL1 &= ~BIT6; // P1SEL1,0 = 01 so to turn bit 6 to do SOMI function
	P1SEL0 |= BIT6;

	PM5CTL0 &= ~LOCKLPM5 // turn on the I/O

	UCA0CTLW0 &= ~UCSWRST;  // turn the system back on, put A0 into SW reset

	// -- Setting of interrupts for: SW1, SW2 and recieved flag
	P4IE |= BIT1; // Interrupt Enable P4.1 IRQ (SW1)
	P4IFG &= ~BIT1; // clear flag

	P2IE |= BIT3; // Interrupt Enable P2.3 IRQ (SW2)
	P2IFG &= ~BIT3; // clear flag

	UCA0IE |= UCRXIE; // enable SPI Rx IRQ
	UCA0IFG &= ~UCRXIFG; // clear flag

	// turn on all de maskable interrupts
	__enable_interrupt();

	while(1){}   // do nothing


	return 0;
}

    // -- Interrupt service Routines
#pragma vector = PORT4_VECTOR
__interrupt void ISR_Port4_S1(void)
{
    UCA0TXBUF = 0x10; // Tx 0x10 out over SPI
    P4IFG &= ~BIT1; // clear flag
}

#pragma vector = PORT2_VECTOR
__interrupt void ISR_Port2_S2(void)
{
    UCA0TXBUF = 0x66; // Tx 0x10 out over SPI
    P2IFG &= ~BIT3; // clear flag
}

#pragma vector = EUSCI_A0_VECTOR   // Data is in A0 SPI buffer
__interrupt void ISR_EUSCI_A0(void)
{
    Rx_Data = UCA0RXBUF;      // read Rx buffer
    if (Rx_Data == 0x10){
        P1OUT ^= BIT0;        // toggle LED1
    } else if (Rx_Data == 0x66){
        P6OUT ^= BIT6;        // toggle LED1
    }
}
