            ORG		    0x3A2	
BEGIN:		WORD		0x5D3	
CUR: 		WORD 	    ? 		
FIRST: 		WORD 	    ? 		
SECOND: 	WORD 	    ? 		
FINISH:	    WORD		0x0D	
START:		CLA				
            LD 		    BEGIN	
            ST 			CUR 	
S0: 		LD 		    (CUR)+ 
            ST 			SECOND
            SWAB 				
            ST 			FIRST 	
W1: 		IN 			7 	
            AND 		#0x40 	
            BEQ 		W1 	
            LD		 	FIRST 	
            CMP 		FINISH	
            OUT 		6 		
            BEQ 		EXIT 	
W2: 		IN 			7 		
            AND 		#0x40 	
            BEQ 		W2 
            LD 		    SECOND
            CMP 		FINISH	
            OUT 		6 		
            BEQ 		EXIT 	
            JUMP 		S0 		
EXIT: 		HLT				
            ORG		    0x5D3
            WORD		0xC3D4
            WORD		0xD1DC
            WORD        0x0D00
