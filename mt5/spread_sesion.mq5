//+------------------------------------------------------------------+
//| spread_sesion.mq5                                                |
//| Mide el coste real de operar: spread historico por hora + la     |
//| comision convertida a pips, y lo compara con stops pequenos.     |
//| Arrastrar sobre un grafico de EURUSD. Imprime en la pestana      |
//| "Expertos". No opera.                                            |
//+------------------------------------------------------------------+
#property script_show_inputs
#property strict

input int    DiasAtras        = 90;   // dias de historial a leer
input int    HusoServidor     = 3;    // GMT del servidor (mira abajo como saberlo)
input int    HusoLocal        = 2;    // GMT tuyo: Madrid es +2 en verano, +1 en invierno
input int    HoraIni          = 8;    // inicio de tu ventana, hora local
input int    MinIni           = 0;
input int    HoraFin          = 11;   // fin de tu ventana, hora local
input int    MinFin           = 30;
input double ComisionPorLote  = 0.0;  // ida y vuelta, por lote, en la divisa de la cuenta

double g_pip;

double Percentil(int &v[], double p)
  {
   int n = ArraySize(v);
   if(n == 0) return 0.0;
   int k = (int)MathFloor(p * (n - 1) + 0.5);
   if(k < 0) k = 0;
   if(k > n - 1) k = n - 1;
   return (double)v[k];
  }

void Resumen(string etiqueta, int &v[])
  {
   int n = ArraySize(v);
   if(n == 0) { PrintFormat("%-14s  sin datos", etiqueta); return; }
   ArraySort(v);
   double suma = 0.0;
   for(int i = 0; i < n; i++) suma += (double)v[i];
   double media = suma / n;
   PrintFormat("%-14s  n=%7d   media %5.2f p   mediana %5.2f p   p90 %5.2f p   max %5.2f p",
               etiqueta, n, media / 10.0, Percentil(v, 0.50) / 10.0,
               Percentil(v, 0.90) / 10.0, Percentil(v, 1.00) / 10.0);
  }

void OnStart()
  {
   int dig = (int)SymbolInfoInteger(_Symbol, SYMBOL_DIGITS);
   g_pip = (dig == 5 || dig == 3) ? 10 * _Point : _Point;

   MqlRates r[];
   ArraySetAsSeries(r, false);
   int copiadas = CopyRates(_Symbol, PERIOD_M1, 0, DiasAtras * 1440, r);
   if(copiadas <= 0)
     {
      Print("No hay historial de M1. Abre un grafico M1 de ", _Symbol,
            ", baja hasta el fondo para que se descargue, y vuelve a lanzarlo.");
      return;
     }

   int ventana[];   ArrayResize(ventana, 0);
   int porHora[24][];
   int cuenta[24];
   for(int h = 0; h < 24; h++) { ArrayResize(porHora[h], 0); cuenta[h] = 0; }

   int desplaza = (HusoLocal - HusoServidor) * 3600;
   int ini = HoraIni * 60 + MinIni;
   int fin = HoraFin * 60 + MinFin;

   for(int i = 0; i < copiadas; i++)
     {
      if(r[i].spread <= 0) continue;
      datetime local = r[i].time + desplaza;
      MqlDateTime t;
      TimeToStruct(local, t);
      if(t.day_of_week == 0 || t.day_of_week == 6) continue;

      int n = ArraySize(porHora[t.hour]);
      ArrayResize(porHora[t.hour], n + 1);
      porHora[t.hour][n] = (int)r[i].spread;

      int m = t.hour * 60 + t.min;
      if(m >= ini && m < fin)
        {
         int k = ArraySize(ventana);
         ArrayResize(ventana, k + 1);
         ventana[k] = (int)r[i].spread;
        }
     }

   Print("======================================================================");
   PrintFormat("COSTE REAL EN %s   ·   %d velas de un minuto leidas", _Symbol, copiadas);
   PrintFormat("hora del servidor ahora: %s   ·   hora GMT ahora: %s",
               TimeToString(TimeCurrent(), TIME_DATE|TIME_MINUTES),
               TimeToString(TimeGMT(), TIME_DATE|TIME_MINUTES));
   Print("si esas dos horas no cuadran con el HusoServidor que has puesto, corrigelo y repite");
   Print("======================================================================");

   Print("");
   Print("SPREAD POR HORA LOCAL");
   for(int h = 0; h < 24; h++)
      if(ArraySize(porHora[h]) > 0)
         Resumen(StringFormat("  %02d:00", h), porHora[h]);

   Print("");
   PrintFormat("TU VENTANA  %02d:%02d - %02d:%02d", HoraIni, MinIni, HoraFin, MinFin);
   Resumen("  ventana", ventana);

   ArraySort(ventana);
   double medio = 0.0;
   int nv = ArraySize(ventana);
   for(int i = 0; i < nv; i++) medio += (double)ventana[i];
   if(nv > 0) medio /= nv;
   double spreadPips = medio / 10.0;

   double tv = SymbolInfoDouble(_Symbol, SYMBOL_TRADE_TICK_VALUE);
   double ts = SymbolInfoDouble(_Symbol, SYMBOL_TRADE_TICK_SIZE);
   double valorPip = (ts > 0) ? tv * (g_pip / ts) : 0.0;
   double comPips  = (valorPip > 0) ? ComisionPorLote / valorPip : 0.0;
   double total    = spreadPips + comPips;

   Print("");
   Print("COSTE TOTAL POR OPERACION");
   PrintFormat("  spread medio en la ventana ...... %5.2f pips", spreadPips);
   PrintFormat("  valor del pip por lote .......... %8.2f %s", valorPip, AccountInfoString(ACCOUNT_CURRENCY));
   PrintFormat("  comision %6.2f por lote ......... %5.2f pips", ComisionPorLote, comPips);
   PrintFormat("  TOTAL ........................... %5.2f pips", total);

   Print("");
   Print("QUE PORCENTAJE DEL RIESGO SE COME, SEGUN EL STOP");
   for(int s = 2; s <= 8; s++)
      PrintFormat("  stop de %d pips ....... %5.1f %% del riesgo", s, 100.0 * total / s);
   Print("");
   Print("referencia: por debajo del 15 % el coste no decide; por encima del 30 % si.");
  }
//+------------------------------------------------------------------+
