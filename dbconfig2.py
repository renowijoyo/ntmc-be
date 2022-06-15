#!/usr/bin/env python
import mysql.connector as mysql


class DBConfig2:
    def connect(self):
        # db = mysql.connect(
        #     host="202.67.14.247",
        #     user="ntmc_ccntmc",
        #     passwd="0uH7kc6ceEYt",
        #     database="ntmc_ccntmc"
        # )

        dbcon = mysql.connect(
            host="202.67.14.247",
            user="ntmc_brimob_id",
            passwd="brimob123!",
            database="ntmc_brimob_id"
        )



        return dbcon
