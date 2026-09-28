// Run inside a checkout of the official lighter-go repository.
package main

import (
    "encoding/hex"
    "encoding/json"
    "os"
    "os/exec"
    "strings"
    "github.com/elliottech/lighter-go/types/txtypes"
)

func main() {
    cases := []map[string]any{}
    for _, skip := range []bool{false, true} {
        attrs := txtypes.L2TxAttributes{}
        if skip { attrs[4] = 1 }
        withdraw := &txtypes.L2WithdrawTxInfo{FromAccountIndex:12, ApiKeyIndex:3, AssetIndex:3, RouteType:1, Amount:(1<<40)+123, ExpiredAt:1700000600000, Nonce:5, L2TxAttributes:attrs}
        approve := &txtypes.L2ApproveIntegratorTxInfo{AccountIndex:12, ApiKeyIndex:3, IntegratorAccountIndex:99, MaxPerpsTakerFee:100, MaxPerpsMakerFee:20, MaxSpotTakerFee:50, MaxSpotMakerFee:10, ApprovalExpiry:1900000000000, ExpiredAt:1700000600000, Nonce:5, L2TxAttributes:attrs}
        for _, tx := range []txtypes.TxInfo{withdraw, approve} {
            hash,err:=tx.Hash(304);if err!=nil{panic(err)}
            entry:=map[string]any{"tx_type":tx.GetTxType(),"payload":tx,"hash":hex.EncodeToString(hash),"skip_nonce":skip}
            if tx.GetTxType()==45 {entry["l1_message"]=approve.GetL1SignatureBody(304)}
            cases=append(cases,entry)
        }
    }
    sha,err:=exec.Command("git","rev-parse","HEAD").Output();if err!=nil{panic(err)}
    encoder:=json.NewEncoder(os.Stdout);encoder.SetIndent("","  ")
    if err:=encoder.Encode(map[string]any{"source":"https://github.com/elliottech/lighter-go","commit":strings.TrimSpace(string(sha)),"chain_id":304,"cases":cases});err!=nil{panic(err)}
}
