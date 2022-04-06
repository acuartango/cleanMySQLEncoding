
This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <https://www.gnu.org/licenses/>.




# clean MySQL Encoding
Normalize MySQL UTF8 database with incorrectly encoded characters inside

This script resolves a common problem:
You have a mysql db encoded in UTF8, but inside you have some strings (not all of them) bad encoded in others encodings.
I had some strings in Latin1 messed with others correctly encoded in UTF8.

You can't change all the database encoding because is not entirely bad encoded, so you need a "intelligent" program that changes only 
bad encoded strings.

This progran uses "ftfy". I've programmed this script in python to ease it's use inside a MySQL DB. The problem of having multimple encodings into a database field is that if you export the DB in a concrete encoding, you could lost some bad encoded characters forever. To avoid this problem we need call "ftfy" without exporting the database. 

# How to use

<pre>
normalizeBD.py -h <host> -p <port> -d <database> -u <username> -P <password> -c <BD charset>
</pre>
