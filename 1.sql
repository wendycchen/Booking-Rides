SELECT * 
FROM bookings, rides
WHERE bookings.rno = rides.rno
AND rides.driver = "whatever@e.com";