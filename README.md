# Booking
```
$ ./book_flight.py --help
Usage: book_flight.py [OPTIONS]

Options:
  --date DATE       Departure date in format YYYY-MM-DD.  [required]
  --from TEXT       Flight from - IATA code  [required]
  --to TEXT         Flight to - IATA code  [required]
  --cheapest        Find cheapest flight. [default]
  --shortest        Find shortest flight.
  --one-way         Book one-way flight. [default]
  --return INTEGER  Book return flight. Specify the length of your stay in
                    destination (count nights).
  -v, --verbose     Print details.
  --help            Show this message and exit.
  ```
