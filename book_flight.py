#!/usr/bin/env python3

import json
from pprint import pprint
from datetime import datetime, date


try:
    import requests
except ImportError as e:
    print('Please install package "requests" (e.q. pip install requests). ({})'.format(e))
    exit(1)
    
try:
    import click
except ImportError as e:
    print('Please install package "click" (e.q. pip install click). ({})'.format(e))
    exit(1)


class Datetime(click.ParamType):
    '''
    A datetime object parsed via datetime.strptime.
    Format specifiers can be found here :
    https://docs.python.org/3/library/datetime.html#strftime-strptime-behavior
    '''

    name = 'date'

    def __init__(self, format):
        self.format = format

    def convert(self, value, param, ctx):
        if value is None:
            return value

        if isinstance(value, datetime):
            return value

        try:
            datetime_value = datetime.strptime(value, self.format)
            return datetime_value
        except ValueError as ex:
            self.fail('Could not parse datetime string "{datetime_str}" formatted as {format} ({ex})'.format(
datetime_str=value, format=self.format, ex=ex,), param, ctx)


@click.command()
@click.option('--date', 'dateFrom', type=Datetime(format='%Y-%m-%d'), help='Departure date in format YYYY-MM-DD.', required=True)
@click.option('--from', 'flyFrom', help='Flight from - IATA code', required=True)
@click.option('--to', 'to', help='Flight to - IATA code', required=True)
@click.option('--cheapest', is_flag=True, help='Find cheapest flight. [default]')
@click.option('--shortest', is_flag=True, default=False, help='Find shortest flight.')
@click.option('--one-way', 'oneway', is_flag=True, help='Book one-way flight. [default]')
@click.option('--return', 'jreturn', type=int, help='Book return flight. Specify the length of your stay in destination (count nights).')
@click.option('-v', '--verbose', is_flag=True, default=False, help='Verbosity')
def book_flight(dateFrom, flyFrom, to, cheapest, shortest, oneway, jreturn, verbose):
    # prepare parameters of the flight
    params = dict(dateFrom=datetime.strftime(dateFrom, '%d/%m/%Y'),
                  flyFrom=flyFrom,
                  to=to)
    if oneway and jreturn:
        print('You have to choose - one-way or return.')
        exit(1)
    if jreturn:
        params.update(typeFlight='round')
        params.update(daysInDestinationFrom=jreturn)
        params.update(daysInDestinationTo=jreturn)
    else:
        params.update(typeFlight='oneway')
    
    if cheapest and shortest:
        print('You have to choose - shortest or cheapest.')
        exit(1)
    if shortest:
        params.update(sort='duration')
    else:
        params.update(sort='price')
    
    # GET possible flights from skypicker
    if verbose:
        print('The following parameters will be used to find the required flight:')
        pprint(params)
        print('-' * 80)
        print()
        print('Searching...')
        print()
        print('-' * 80)
    try:
        req = requests.get('https://api.skypicker.com/flights', params=params)
    except requests.exceptions.RequestException as e:
        print('Error during flight search ({}).'.format(e))
        exit(1)
    
    js = req.json()
    flights = js.get('data')
    if flights:
        # choose the first flight by - cheapest/shortest
        # TODO: check cheapest from shortest?
        flight = flights[0]
    else:
        print('There if no flight meeting the required criteria.')
        print('Update your requirments and try again.')
        exit(1)
    
    booking_token = flight['booking_token']
    price = flight['price']
    currency = js['currency']
    
    if verbose:
        print('Flight details:')
        print('''id: {}
airlines: {}
flyFrom: {}
flyTo: {}
fly_duration: {}
price: {} {}'''.format(flight['id'],
                    flight['airlines'],
                    flight['flyFrom'],
                    flight['flyTo'],
                    flight['fly_duration'],
                    flight['price'], currency))
        if jreturn:
            print('nightsInDest: {}'.format(flight['nightsInDest']))
        print('-' * 80)
        print()
    
    # http://docs.skypickerbookingapi1.apiary.io/#reference/save-booking/savebooking/save_booking
    data = {'currency': 'EUR',
            'booking_token': booking_token,
            'passengers': [{'firstName': 'Vasek',
                            'documentID': 'ID123',
                            'birthday': '1900-12-20',
                            'email': 'kelidas@centrum.cz',
                            'title': 'Mr',
                            'lastName': 'Sadilek'}]
            }
                
    headers = {'Content-Type': 'application/json'}
    try:
        req = requests.post('http://37.139.6.125:8080/booking', data=json.dumps(data), headers=headers)
    except requests.exceptions.RequestException as e:
        print('Error during flight booking ({}).'.format(e))
        exit(1)
    
    confirm = req.json()
    pnr = confirm.get('pnr')
    if pnr:
        if verbose:
            print('The flight was succesfully booked under the PNR number {}.'.format(pnr))
        else: print(pnr)
    else:
        print('Booking was not succesfull. Please call +420 228-885-100.')

if __name__ == '__main__':
    book_flight()
