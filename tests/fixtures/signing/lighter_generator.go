package main
import (
 "encoding/json"
 "encoding/hex"
 "os"
 "os/exec"
 "strings"
 g "github.com/elliottech/poseidon_crypto/field/goldilocks"
 p2 "github.com/elliottech/poseidon_crypto/hash/poseidon2_goldilocks_plonky2"
 "github.com/elliottech/lighter-go/types/txtypes"
)
func main() {
 orders := []*txtypes.OrderInfo{
 {MarketIndex:1, ClientOrderIndex:42, BaseAmount:1000, Price:250000, IsAsk:0, Type:0, TimeInForce:1, ReduceOnly:0, TriggerPrice:0, OrderExpiry:1800000000000},
 {MarketIndex:1, ClientOrderIndex:43, BaseAmount:0, Price:240000, IsAsk:1, Type:2, TimeInForce:0, ReduceOnly:1, TriggerPrice:245000, OrderExpiry:1800000000000},
 {MarketIndex:1, ClientOrderIndex:44, BaseAmount:0, Price:270000, IsAsk:1, Type:4, TimeInForce:0, ReduceOnly:1, TriggerPrice:265000, OrderExpiry:1800000000000},
 }
 cases := []map[string]any{}
 for _, group := range [][]*txtypes.OrderInfo{orders[:1],orders[:2],orders, {orders[2],orders[1],orders[0]}} {
  fields:=[][]uint64{}
  folded:=p2.EmptyHashOut()
  for i,o:=range group {
   row:=[]g.GoldilocksField{g.GoldilocksField(o.MarketIndex),g.GoldilocksField(o.ClientOrderIndex),g.GoldilocksField(o.BaseAmount),g.GoldilocksField(o.Price),g.GoldilocksField(o.IsAsk),g.GoldilocksField(o.Type),g.GoldilocksField(o.TimeInForce),g.GoldilocksField(o.ReduceOnly),g.GoldilocksField(o.TriggerPrice),g.GoldilocksField(o.OrderExpiry)}
   ints:=[]uint64{};for _,v:=range row{ints=append(ints,uint64(v))};fields=append(fields,ints)
   h:=p2.HashNoPad(row);if i==0{folded=h}else{folded=p2.HashNToOne([]p2.HashOut{folded,h})}
  }
  tx:=txtypes.L2CreateGroupedOrdersTxInfo{AccountIndex:12,ApiKeyIndex:3,GroupingType:3,Orders:group,ExpiredAt:1700000600000,Nonce:5}
  hash,err:=tx.Hash(304);if err!=nil{panic(err)}
  cases=append(cases,map[string]any{"orders":fields,"folded":folded,"transaction_hash":hex.EncodeToString(hash)})
 }
 sha,err:=exec.Command("git","rev-parse","HEAD").Output();if err!=nil{panic(err)}
 enc:=json.NewEncoder(os.Stdout);enc.SetIndent("","  ");enc.Encode(map[string]any{"source":"https://github.com/elliottech/lighter-go","commit":strings.TrimSpace(string(sha)),"poseidon_crypto":"v0.0.15","transaction_prefix":[]uint64{304,28,5,1700000600000,12,3,3},"cases":cases})
}
