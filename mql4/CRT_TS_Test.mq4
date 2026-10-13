//+------------------------------------------------------------------+
//|  CRT_TS_Test.mq4                                                 |
//|                                                                  |
//|  Mide el indicador CRT_Turtle_Soup en el Strategy Tester de MT4. |
//|                                                                  |
//|  Un indicador NO se backtestea: el Tester solo prueba Expert     |
//|  Advisors. Esto es el EA que lee los buffers del indicador con   |
//|  iCustom() y opera sus señales, para que el Tester pueda dar un  |
//|  numero sobre SU codigo y no sobre una reimplementacion.         |
//|                                                                  |
//|  SE USA EN DOS PASADAS:                                          |
//|                                                                  |
//|  1 · DIAGNOSTICO. Deja ModoDiagnostico=true y pasalo por el      |
//|      Tester un mes. En la pestaña «Diario» saldra, por cada vela |
//|      con señal, que buffer se ha encendido y con que valor. Con  |
//|      eso se sabe cual es la compra y cual la venta.              |
//|                                                                  |
//|  2 · MEDICION. Pon ModoDiagnostico=false, mete los numeros de    |
//|      buffer que hayan salido, y pasalo por los años que quieras. |
//|                                                                  |
//|  IMPORTANTE sobre el Tester:                                     |
//|   · Modelado «Cada tick». Con «Solo precios de apertura» en M5   |
//|     los resultados no valen nada.                                |
//|   · Mira la «calidad del modelado» al acabar. Por debajo del     |
//|     90 % no te fies.                                             |
//|   · Pon el spread real de tu broker, no el de por defecto.       |
//|   · El indicador tiene que estar en MQL4/Indicators compilado.   |
//|                                                                  |
//|  Escrito sin poder compilarlo. Si MetaEditor se queja, pega el   |
//|  error y se arregla.                                             |
//+------------------------------------------------------------------+
#property strict
#property copyright "Fondeo"
#property description "Mide el indicador CRT Turtle Soup en el Strategy Tester"

//--- que indicador se mide -------------------------------------------------
extern string  s1                = "--- el indicador ---";
extern string  NombreIndicador   = "CRT_Turtle_Soup_v8";
extern bool    ModoDiagnostico   = true;    // primera pasada: solo mirar buffers
extern int     BuffersAExplorar  = 8;
extern int     BufferCompra      = 0;       // se rellenan tras el diagnostico
extern int     BufferVenta       = 1;

//--- como se opera la señal ------------------------------------------------
extern string  s2                = "--- la operacion ---";
extern double  RatioObjetivo     = 2.0;     // 1:R
extern int     ModoStop          = 0;       // 0 = extremo de la vela de señal
                                            // 1 = pips fijos
extern double  StopPips          = 6.0;
extern double  ColchonPips       = 0.5;     // se añade al extremo
extern double  RiesgoPorcentaje  = 1.0;
extern int     MaxOperaciones    = 1;       // posiciones vivas a la vez

//--- cuando se opera -------------------------------------------------------
extern string  s3                = "--- la ventana ---";
extern bool    UsarVentana       = false;
extern int     HoraInicio        = 8;       // hora del servidor
extern int     HoraFin           = 12;
extern bool    CerrarAlFinal     = false;   // cerrar todo al salir de la ventana

extern string  s4                = "--- varios ---";
extern int     NumeroMagico      = 770801;
extern int     Deslizamiento     = 3;

datetime g_ultimaVela = 0;
int      g_digitos;
double   g_pip;

//+------------------------------------------------------------------+
int OnInit()
  {
   g_digitos = (int)MarketInfo(Symbol(), MODE_DIGITS);
   g_pip = (g_digitos == 5 || g_digitos == 3) ? Point * 10 : Point;
   if(ModoDiagnostico)
      Print("DIAGNOSTICO activo · se listaran los buffers 0..", BuffersAExplorar - 1,
            " del indicador ", NombreIndicador);
   return(INIT_SUCCEEDED);
  }

//+------------------------------------------------------------------+
//| Lee un buffer del indicador. Si se omiten sus parametros, MT4    |
//| usa los que el indicador trae por defecto.                       |
//+------------------------------------------------------------------+
double Buf(int indice, int desplazamiento)
  {
   return(iCustom(Symbol(), Period(), NombreIndicador, indice, desplazamiento));
  }

bool Encendido(double v)
  {
   return(v != EMPTY_VALUE && v != 0.0 && MathAbs(v) < 1.0e10);
  }

//+------------------------------------------------------------------+
int Vivas()
  {
   int n = 0;
   for(int i = OrdersTotal() - 1; i >= 0; i--)
     {
      if(!OrderSelect(i, SELECT_BY_POS, MODE_TRADES)) continue;
      if(OrderSymbol() == Symbol() && OrderMagicNumber() == NumeroMagico) n++;
     }
   return(n);
  }

void CerrarTodo()
  {
   for(int i = OrdersTotal() - 1; i >= 0; i--)
     {
      if(!OrderSelect(i, SELECT_BY_POS, MODE_TRADES)) continue;
      if(OrderSymbol() != Symbol() || OrderMagicNumber() != NumeroMagico) continue;
      double precio = (OrderType() == OP_BUY) ? Bid : Ask;
      if(!OrderClose(OrderTicket(), OrderLots(), precio, Deslizamiento))
         Print("no se pudo cerrar: ", GetLastError());
     }
  }

//+------------------------------------------------------------------+
//| Lotes para arriesgar el % elegido con ESE stop concreto.         |
//+------------------------------------------------------------------+
double Lotes(double distanciaPrecio)
  {
   double valorTick = MarketInfo(Symbol(), MODE_TICKVALUE);
   double tamTick   = MarketInfo(Symbol(), MODE_TICKSIZE);
   if(valorTick <= 0 || tamTick <= 0 || distanciaPrecio <= 0) return(0);
   double riesgo = AccountBalance() * RiesgoPorcentaje / 100.0;
   double porLote = (distanciaPrecio / tamTick) * valorTick;
   if(porLote <= 0) return(0);
   double lotes = riesgo / porLote;
   double minLote  = MarketInfo(Symbol(), MODE_MINLOT);
   double maxLote  = MarketInfo(Symbol(), MODE_MAXLOT);
   double pasoLote = MarketInfo(Symbol(), MODE_LOTSTEP);
   if(pasoLote > 0) lotes = MathFloor(lotes / pasoLote) * pasoLote;
   if(lotes < minLote) lotes = 0;            // mejor no operar que redondear arriba
   if(lotes > maxLote) lotes = maxLote;
   return(NormalizeDouble(lotes, 2));
  }

//+------------------------------------------------------------------+
void Abre(int tipo, double stop)
  {
   double entrada = (tipo == OP_BUY) ? Ask : Bid;
   double dist = MathAbs(entrada - stop);
   double minStop = MarketInfo(Symbol(), MODE_STOPLEVEL) * Point;
   if(dist < minStop || dist <= 0)
     {
      Print("stop demasiado pegado para el broker: ", DoubleToString(dist / g_pip, 1),
            " pips · minimo ", DoubleToString(minStop / g_pip, 1));
      return;
     }
   double objetivo = (tipo == OP_BUY) ? entrada + RatioObjetivo * dist
                                      : entrada - RatioObjetivo * dist;
   double lotes = Lotes(dist);
   if(lotes <= 0) { Print("lotaje 0 con ese stop, no se abre"); return; }
   int t = OrderSend(Symbol(), tipo, lotes, NormalizeDouble(entrada, g_digitos),
                     Deslizamiento, NormalizeDouble(stop, g_digitos),
                     NormalizeDouble(objetivo, g_digitos),
                     "CRT TS", NumeroMagico, 0, clrNONE);
   if(t < 0) Print("OrderSend fallo: ", GetLastError());
  }

//+------------------------------------------------------------------+
void OnTick()
  {
   if(Time[0] == g_ultimaVela) return;        // una decision por vela cerrada
   g_ultimaVela = Time[0];

   //--- primera pasada: solo mirar que buffers se encienden ---------------
   if(ModoDiagnostico)
     {
      string linea = "";
      for(int b = 0; b < BuffersAExplorar; b++)
        {
         double v = Buf(b, 1);
         if(Encendido(v))
            linea = linea + "  buffer " + IntegerToString(b) + " = " +
                    DoubleToString(v, g_digitos);
        }
      if(linea != "")
         Print(TimeToString(Time[1], TIME_DATE | TIME_MINUTES), linea,
               "   [O ", DoubleToString(Open[1], g_digitos),
               " H ", DoubleToString(High[1], g_digitos),
               " L ", DoubleToString(Low[1], g_digitos),
               " C ", DoubleToString(Close[1], g_digitos), "]");
      return;
     }

   //--- ventana horaria ---------------------------------------------------
   bool dentro = true;
   if(UsarVentana)
     {
      int h = TimeHour(Time[0]);
      dentro = (HoraInicio < HoraFin) ? (h >= HoraInicio && h < HoraFin)
                                      : (h >= HoraInicio || h < HoraFin);
      if(!dentro && CerrarAlFinal) CerrarTodo();
     }
   if(!dentro) return;
   if(Vivas() >= MaxOperaciones) return;

   //--- la señal, leida de la vela YA CERRADA ----------------------------
   double compra = Buf(BufferCompra, 1);
   double venta  = Buf(BufferVenta,  1);
   bool hayCompra = Encendido(compra);
   bool hayVenta  = Encendido(venta);
   if(hayCompra && hayVenta) return;          // señal ambigua, se descarta
   if(!hayCompra && !hayVenta) return;

   double stop;
   if(ModoStop == 1)
      stop = hayCompra ? Ask - StopPips * g_pip : Bid + StopPips * g_pip;
   else
      stop = hayCompra ? Low[1] - ColchonPips * g_pip
                       : High[1] + ColchonPips * g_pip;

   Abre(hayCompra ? OP_BUY : OP_SELL, stop);
  }
//+------------------------------------------------------------------+
