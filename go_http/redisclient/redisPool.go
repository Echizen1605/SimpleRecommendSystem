package redisclient

import (
	redigo "github.com/garyburd/redigo/redis"
)

var pool *redigo.Pool

func init() {
	pool_size := 20
	pool = redigo.NewPool(func() (redigo.Conn, error) {
		c, err := redigo.Dial("tcp", "127.0.0.1:6379", redigo.DialDatabase(5), redigo.DialPassword(""))
		if err != nil {
			return nil, err
		}
		return c, nil
	}, pool_size)
}
func Get() redigo.Conn {
	return pool.Get()
}
