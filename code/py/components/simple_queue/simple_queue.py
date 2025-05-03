class SimpleQueue:
    """
    A simple queue implementation with a fixed size.
    When the queue is full, the oldest element is removed to make space for the new one.
    """
    _max_size: int = 0
    _queue: list = []

    def __init__(self, max_size: int) -> None:
        assert max_size > 0
        self._max_size = max_size


    def __str__(self) -> str:
        return str(self._queue)


    def enqueue(self, data) -> None:
        """
        Add an element to the queue. If the queue is full, remove the oldest element.
        
        :param data: The element to add to the queue.
        
        :return: None
        """
        assert data is not None
        if self.current_number_of_elements() >= self._max_size:
            print(f"Queue (size: {self._max_size}) is full, removing oldest element..")
            self._queue.pop(0)

        self._queue.append(data)


    def dequeue(self) -> Any:
        """
        Remove and return the oldest element from the queue.
        If the queue is empty, return None.
        
        :return: The oldest element in the queue, or None if the queue is empty.
        """
        if self.current_number_of_elements() == 0:
            return None

        return self._queue.pop(0)


    def current_number_of_elements(self) -> int:
        """
        Get the current number of elements in the queue.
        
        :return: The number of elements in the queue.
        """
        return len(self._queue)


    def get_max_number_of_elements(self) -> int:
        """
        Get the maximum number of elements the queue can hold.
        
        :return: The maximum number of elements in the queue.
        """
        return self._max_size
