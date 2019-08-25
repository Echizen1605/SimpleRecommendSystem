package main

import (
	"fmt"
	"html/template"
	"log"
	"net/http"
	"sort"
	"strconv"
    "time"

	"./redisclient"
	"github.com/garyburd/redigo/redis"
	"github.com/yanyiwu/gojieba"
)

var jieba = gojieba.NewJieba()
var c = redisclient.Get()

func checkErr(err error) {
	if err != nil {
		log.Println(err)
	}
}

type UserData struct {
	SearchText string
	Content    string
}

func renderHTML(w http.ResponseWriter, file string, data interface{}) {
	t, err := template.New(file).ParseFiles("views/" + file)
	checkErr(err)
	t.Execute(w, data)
}

func index(w http.ResponseWriter, r *http.Request) {
	if r.Method == "POST" {
		if err := r.ParseForm(); err != nil {
			log.Println("Handler:page:ParseForm: ", err)
		}

		u := UserData{}
		u.SearchText = r.Form.Get("SearchText")

        now := time.Now().UnixNano() / 1e6

		keywords := jieba.ExtractWithWeight(u.SearchText, 5)
		fmt.Println(keywords)

		resultMap := make(map[string]float64)
		var resultContent = ""

		c.Do("SELECT", 5)

		for _, v := range keywords {
			res, _ := redis.StringMap(c.Do("ZREVRANGE", v.Word, 0, -1, "WITHSCORES"))
			// fmt.Println(len(res))
			for key := range res {
				curScore, _ := strconv.ParseFloat(res[key], 64)
				if _, ok := resultMap[key]; ok {
					resultMap[key] += curScore * float64(v.Weight)
				} else {
					resultMap[key] = curScore * float64(v.Weight)
				}
			}
		}

		newMap := make(map[float64]string, len(resultMap))
		var values []float64
		for key := range resultMap {
			newMap[resultMap[key]] = key
			values = append(values, resultMap[key])
		}
		sort.Sort(sort.Reverse(sort.Float64Slice(values)))

		c.Do("SELECT", 6)
		for index, eachValue := range values {
			if index > 59 {
				break
			}
			resultContent += fmt.Sprintf("推荐%d:\n", index+1)
			content, _ := redis.String(c.Do("HGET", "article_detail", newMap[eachValue]))
			resultContent += fmt.Sprintf("%s\n\n", content)
		}

        fmt.Printf("耗时%dms\n\n", time.Now().UnixNano()/1e6 - now)

		u.Content = resultContent
		renderHTML(w, "index.html", u)
	} else {
		u := UserData{}
		u.SearchText = ""
		u.Content = ""
		renderHTML(w, "index.html", u)
	}
}

func main() {
	http.HandleFunc("/", index)
    err := http.ListenAndServe("192.168.8.98:9090", nil)
	if err != nil {
		log.Fatal("ListenAndServe: ", err)
	}
}
