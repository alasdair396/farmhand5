import sqlite3

connection = sqlite3.connect('droid.db')

def update_droid_row(id,droid_name,droid_id,droid_description, feed_density, droid_server):
    sql_statement = f'''
        UPDATE droid
        SET droid_name=     '{droid_name}',
        droid_id=           '{droid_id}',
        droid_description=  '{droid_description}',
        feed_density=       '{feed_density}',
        droid_server=       '{droid_server}'
        WHERE
        id = '{id}
    '''


#
    sql_statement = f'''
        UPDATE droid
        SET droid_name=     '{droid_name}',
        droid_id=           '{droid_id}',
        droid_description=  '{droid_description}',
        feed_density=       '{feed_density}',
        droid_server=       '{droid_server}'
        WHERE
        id = '{id}
        '''
    print(sql_statement)
    connection.execute(sql_statement)
    #connection.commit()