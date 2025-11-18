#ifndef TASK_HPP
#define TASK_HPP

#include <coroutine>
#include <exception>
#include <optional>

template<typename T>
struct Task {
    struct promise_type {
        std::optional<T> result;
        std::exception_ptr exception;

        Task get_return_object() {
            return Task{std::coroutine_handle<promise_type>::from_promise(*this)};
        }

        std::suspend_always initial_suspend() { return {}; }
        std::suspend_always final_suspend() noexcept { return {}; }

        void return_value(T value) {
            result = std::move(value);
        }

        void unhandled_exception() {
            exception = std::current_exception();
        }
    };

    std::coroutine_handle<promise_type> handle;

    Task(std::coroutine_handle<promise_type> h) : handle(h) {}
    ~Task() {
        if (handle) handle.destroy();
    }

    // Move only
    Task(const Task&) = delete;
    Task& operator=(const Task&) = delete;
    Task(Task&& other) : handle(other.handle) { other.handle = nullptr; }
    Task& operator=(Task&& other) {
        if (this != &other) {
            if (handle) handle.destroy();
            handle = other.handle;
            other.handle = nullptr;
        }
        return *this;
    }

    bool await_ready() { return false; }

    void await_suspend(std::coroutine_handle<> awaiting) {
        // Resume this coroutine
        handle.resume();
    }

    T await_resume() {
        if (handle.promise().exception) {
            std::rethrow_exception(handle.promise().exception);
        }
        return std::move(*handle.promise().result);
    }

    T get() {
        handle.resume();
        return await_resume();
    }
};

// Specialization for void
template<>
struct Task<void> {
    struct promise_type {
        std::exception_ptr exception;

        Task get_return_object() {
            return Task{std::coroutine_handle<promise_type>::from_promise(*this)};
        }

        std::suspend_always initial_suspend() { return {}; }
        std::suspend_always final_suspend() noexcept { return {}; }

        void return_void() {}

        void unhandled_exception() {
            exception = std::current_exception();
        }
    };

    std::coroutine_handle<promise_type> handle;

    Task(std::coroutine_handle<promise_type> h) : handle(h) {}
    ~Task() {
        if (handle) handle.destroy();
    }

    Task(const Task&) = delete;
    Task& operator=(const Task&) = delete;
    Task(Task&& other) : handle(other.handle) { other.handle = nullptr; }
    Task& operator=(Task&& other) {
        if (this != &other) {
            if (handle) handle.destroy();
            handle = other.handle;
            other.handle = nullptr;
        }
        return *this;
    }

    bool await_ready() { return false; }

    void await_suspend(std::coroutine_handle<> awaiting) {
        handle.resume();
    }

    void await_resume() {
        if (handle.promise().exception) {
            std::rethrow_exception(handle.promise().exception);
        }
    }

    void get() {
        handle.resume();
        await_resume();
    }
};

#endif // TASK_HPP
